use std::path::PathBuf;

use diesel::{QueryDsl, RunQueryDsl};
use juniper::{FieldError, FieldResult};

use file::FileContentInput;
use problem::material::Material;
use problem::ProblemName;
use root::ApiContext;
use schema::problems;
use user::UserId;

use crate::api::award::{AwardView, ScoreAwardGrading};
use crate::data::award::{
    AwardDomain, AwardValue, ScoreAwardDomain, ScoreAwardGrade, ScoreAwardValue, ScoreRange,
};

use super::*;
use crate::api::contest::{Contest, ContestStatus};
use crate::api::contest_evaluation::Evaluation;
use crate::api::contest_submission::{FileInput, Submission};

#[derive(juniper::GraphQLInputObject)]
pub struct ProblemInput {
    pub name: String,
    pub archive_content: FileContentInput,
}

#[derive(Insertable)]
#[table_name = "problems"]
pub struct ProblemInsertable {
    name: String,
    archive_integrity: String,
}

#[derive(juniper::GraphQLInputObject)]
pub struct ProblemUpdateInput {
    name: String,
    archive_content: Option<FileContentInput>,
}

#[derive(AsChangeset)]
#[table_name = "problems"]
pub struct ProblemChangeset {
    archive_integrity: Option<String>,
}

#[derive(Queryable, Clone, Debug)]
struct ProblemData {
    name: String,
    archive_integrity: String,
}

/// A problem in the contest
#[derive(Clone)]
pub struct Problem {
    contest: Contest,
    data: ProblemData,
}

#[juniper_ext::graphql(Context = ApiContext)]
impl Problem {
    /// The contest this problem belongs to.
    pub fn contest(&self) -> &Contest {
        &self.contest
    }

    /// Name of this problem. Unique in the current contest.
    pub fn name(&self) -> ProblemName {
        ProblemName(self.data.name.clone())
    }

    /// Material of this problem
    pub fn material(&self, context: &ApiContext) -> FieldResult<Material> {
        let mut cache = context.material_cache.borrow_mut();

        let key = &self.data.archive_integrity;
        if !cache.contains_key(key) {
            (*cache).insert(
                key.to_owned(),
                task_maker::generate_material(self.unpack(context)?)?,
            );
        }

        Ok((*cache.get(key).unwrap()).clone())
    }

    /// Range of the total score, obtained as the sum of all the score awards
    pub fn score_range(&self, context: &ApiContext) -> FieldResult<ScoreRange> {
        Ok(ScoreRange::total(
            self.material(context)?
                .awards
                .iter()
                .filter_map(|award| match award.material.domain {
                    AwardDomain::Score(ScoreAwardDomain { range }) => Some(range),
                    _ => None,
                }),
        ))
    }

    pub fn score_domain(&self, context: &ApiContext) -> FieldResult<ScoreAwardDomain> {
        Ok(ScoreAwardDomain {
            range: self.score_range(context)?,
        })
    }

    pub fn view(&self, context: &ApiContext, user_id: Option<UserId>) -> FieldResult<ProblemView> {
        context.authorize_user(&user_id)?;
        Ok(ProblemView {
            problem: (*self).clone(),
            user_id,
        })
    }
}

impl Problem {
    fn new(context: &ApiContext, data: ProblemData) -> FieldResult<Self> {
        let contest = Contest::current(context)?;
        Ok(Problem { contest, data })
    }

    /// Get a problem data by its name
    pub fn by_name(context: &ApiContext, name: &str) -> FieldResult<Self> {
        let data = problems::table.find(name).first(&context.database)?;
        Ok(Self::new(context, data)?)
    }

    /// Get all the problems data in the database
    pub fn all(context: &ApiContext) -> FieldResult<Vec<Self>> {
        Ok(problems::table
            .load::<ProblemData>(&context.database)?
            .into_iter()
            .map(|data| Self::new(context, data))
            .collect::<Result<Vec<_>, _>>()?)
    }

    /// Insert a problem in the database
    pub fn insert(context: &ApiContext, inputs: Vec<ProblemInput>) -> FieldResult<()> {
        for ProblemInput {
            name,
            archive_content,
        } in inputs
        {
            diesel::insert_into(problems::table)
                .values(ProblemInsertable {
                    name,
                    archive_integrity: context.create_blob(&archive_content.decode()?)?,
                })
                .execute(&context.database)?;
        }
        Ok(())
    }

    /// Delete a problem from the database
    pub fn delete(context: &ApiContext, names: Vec<String>) -> FieldResult<()> {
        use crate::diesel::ExpressionMethods;
        diesel::delete(problems::table)
            .filter(problems::dsl::name.eq_any(names))
            .execute(&context.database)?;
        Ok(())
    }

    /// Update a problem in the database
    pub fn update(context: &ApiContext, inputs: Vec<ProblemUpdateInput>) -> FieldResult<()> {
        use crate::diesel::ExpressionMethods;
        for input in inputs {
            diesel::update(problems::table)
                .filter(problems::dsl::name.eq(&input.name))
                .set(&ProblemChangeset {
                    archive_integrity: if let Some(content) = input.archive_content {
                        Some(context.create_blob(&content.decode()?)?)
                    } else {
                        None
                    },
                })
                .execute(&context.database)?;
        }
        Ok(())
    }

    pub fn unpack(&self, context: &ApiContext) -> FieldResult<PathBuf> {
        context.unpack_archive(&self.data.archive_integrity, "problem")
    }
}

/// A problem in the contest as seen by contestants
#[derive(Clone)]
pub struct ProblemView {
    problem: Problem,
    user_id: Option<UserId>,
}

#[juniper_ext::graphql(Context = ApiContext)]
impl ProblemView {
    pub fn awards(&self, context: &ApiContext) -> FieldResult<Vec<AwardView>> {
        Ok(self
            .problem
            .material(context)?
            .awards
            .iter()
            .map(|award| AwardView {
                user_id: self.user_id.clone(),
                award: (*award).clone(),
                problem: self.problem.clone(),
            })
            .collect())
    }

    pub fn grading(&self, context: &ApiContext) -> FieldResult<ScoreAwardGrading> {
        Ok(ScoreAwardGrading {
            domain: self.problem.score_domain(context)?,
            grade: match self.tackling() {
                Some(t) => Some(t.grade(context)?),
                None => None,
            },
        })
    }

    pub fn tackling(&self) -> Option<ProblemTackling> {
        // TODO: return `None` if user is not participating in the contest
        self.user_id.as_ref().map(|user_id| ProblemTackling {
            problem: self.problem.clone(),
            user_id: (*user_id).clone(),
        })
    }
}

/// Progress at solving a problem by a user in the contest
pub struct ProblemTackling {
    problem: Problem,
    user_id: UserId,
}

impl ProblemTackling {
    pub fn submit(&self, context: &ApiContext, files: Vec<FileInput>) -> FieldResult<Submission> {
        if !self.can_submit() {
            return Err("cannot submit now".into());
        }

        let submission =
            Submission::insert(&context, &self.user_id.0, &self.problem.name().0, files)?;
        Evaluation::start_new(&submission, context)?;
        Ok(submission)
    }
}

/// Attempts at solving a problem by a user in the contest
#[juniper_ext::graphql(Context = ApiContext)]
impl ProblemTackling {
    /// Sum of the score awards
    pub fn score(&self, context: &ApiContext) -> FieldResult<ScoreAwardValue> {
        Ok(ScoreAwardValue::total(
            self.problem
                .view(context, Some(self.user_id.clone()))?
                .awards(context)?
                .into_iter()
                .map(|award_view: AwardView| -> FieldResult<_> {
                    Ok(
                        match award_view
                            .tackling()
                            .ok_or(FieldError::from("problem tackling without award tackling"))?
                            .best_achievement(context)?
                            .value()
                        {
                            AwardValue::Score(value) => Some(value),
                            _ => None,
                        },
                    )
                })
                .filter_map(|x| match x {
                    Ok(None) => None,
                    Ok(Some(x)) => Some(Ok(x)),
                    Err(x) => Some(Err(x)),
                })
                .collect::<FieldResult<Vec<_>>>()?,
        ))
    }

    fn grade(&self, context: &ApiContext) -> FieldResult<ScoreAwardGrade> {
        Ok(ScoreAwardGrade {
            domain: self.problem.score_domain(context)?,
            value: self.score(context)?,
        })
    }

    /// Submissions of the current user (if to be shown)
    fn submissions(
        &self,
        context: &ApiContext,
    ) -> FieldResult<Vec<contest_submission::Submission>> {
        Ok(contest_submission::Submission::by_user_and_problem(
            context,
            &self.user_id.0,
            &self.problem.name().0,
        )?)
    }

    /// Indicates if the user can submit to this problem
    fn can_submit(&self) -> bool {
        match self.problem.contest.status() {
            ContestStatus::Running => true,
            _ => false,
        }
    }
}
