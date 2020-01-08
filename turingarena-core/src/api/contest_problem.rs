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
use crate::api::contest::{Contest, ContestStatus, ContestView};
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
pub struct Problem {
    contest: Contest,
    data: ProblemData,
    material: Material,
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
    pub fn material(&self) -> &Material {
        &self.material
    }

    /// Range of the total score, obtained as the sum of all the score awards
    pub fn score_range(&self) -> ScoreRange {
        ScoreRange::total(self.material.awards.iter().filter_map(
            |award| match award.material.domain {
                AwardDomain::Score(ScoreAwardDomain { range }) => Some(range),
                _ => None,
            },
        ))
    }

    pub fn score_domain(&self) -> ScoreAwardDomain {
        ScoreAwardDomain {
            range: self.score_range(),
        }
    }

    pub fn view(&self, user_id: Option<UserId>) -> ProblemView {
        ProblemView {
            problem: &self,
            user_id,
        }
    }
}

impl Problem {
    fn new(context: &ApiContext, data: ProblemData) -> FieldResult<Self> {
        let material = Self::get_problem_material(&data, context)?;
        let contest = Contest::current(context)?;
        Ok(Problem {
            contest,
            data,
            material,
        })
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
        Self::unpack_data(&self.data, context)
    }

    fn unpack_data(data: &ProblemData, context: &ApiContext) -> FieldResult<PathBuf> {
        context.unpack_archive(&data.archive_integrity, "problem")
    }

    /// Material of this problem
    fn get_problem_material(data: &ProblemData, context: &ApiContext) -> FieldResult<Material> {
        Ok(task_maker::generate_material(Self::unpack_data(
            data, context,
        )?)?)
    }
}

/// A problem in the contest as seen by contestants
pub struct ProblemView<'a> {
    problem: &'a Problem,
    user_id: Option<UserId>,
}

#[juniper_ext::graphql(Context = ApiContext)]
impl<'a> ProblemView<'a> {
    pub fn awards(&self) -> Vec<AwardView> {
        self.problem
            .material()
            .awards
            .iter()
            .map(|award| AwardView {
                user_id: self.user_id.clone(),
                award: (*award).clone(),
                problem: self.problem,
            })
            .collect()
    }

    pub fn grading(&self, context: &ApiContext) -> FieldResult<ScoreAwardGrading> {
        Ok(ScoreAwardGrading {
            domain: self.problem.score_domain(),
            grade: match self.tackling() {
                Some(t) => Some(t.grade(context)?),
                None => None,
            },
        })
    }

    pub fn tackling(&self) -> Option<ProblemTackling<'a>> {
        // TODO: return `None` if user is not participating in the contest
        self.user_id.as_ref().map(|user_id| ProblemTackling {
            problem: &self.problem,
            user_id: (*user_id).clone(),
        })
    }
}

/// Progress at solving a problem by a user in the contest
pub struct ProblemTackling<'a> {
    problem: &'a Problem,
    user_id: UserId,
}

impl ProblemTackling<'_> {
    pub fn submit(&self, context: &ApiContext, files: Vec<FileInput>) -> FieldResult<Submission> {
        if self.can_submit() {
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
impl ProblemTackling<'_> {
    /// Sum of the score awards
    pub fn score(&self, context: &ApiContext) -> FieldResult<ScoreAwardValue> {
        Ok(ScoreAwardValue::total(
            self.problem
                .view(Some(self.user_id.clone()))
                .awards()
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
            domain: self.problem.score_domain(),
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
