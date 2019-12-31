use std::path::PathBuf;

use diesel::{QueryDsl, RunQueryDsl};
use juniper::FieldResult;

use file::FileContentInput;
use problem::material::Material;
use problem::ProblemName;
use root::ApiContext;
use schema::problems;
use user::UserId;

use crate::api::award::AwardOutcome;
use crate::data::file::FileContent;

use super::contest::ContestView;
use super::*;

#[derive(juniper::GraphQLInputObject, Insertable)]
#[table_name = "problems"]
pub struct ProblemInput {
    name: String,
    archive_content: FileContentInput,
}

#[derive(juniper::GraphQLInputObject, AsChangeset)]
#[table_name = "problems"]
pub struct ProblemUpdateInput {
    name: String,
    archive_content: Option<FileContentInput>,
}

#[derive(Queryable, Clone, Debug)]
struct ProblemData {
    name: String,
    archive_content: FileContent,
}

/// A problem in the contest
pub struct Problem<'a> {
    context: &'a ApiContext<'a>,
    data: ProblemData,
    material: Material,
}

#[juniper_ext::graphql]
impl Problem<'_> {
    /// Name of this problem. Unique in the current contest.
    fn name(&self) -> ProblemName {
        ProblemName(self.data.name.clone())
    }

    /// Material of this problem
    fn material(&self) -> &Material {
        &self.material
    }
}

impl<'a> Problem<'a> {
    fn new(context: &'a ApiContext<'a>, data: ProblemData) -> FieldResult<Self> {
        let material = Self::get_problem_material(&data, context)?;
        Ok(Problem {
            context,
            data,
            material,
        })
    }

    /// Get a problem data by its name
    pub fn by_name(context: &'a ApiContext<'a>, name: &str) -> FieldResult<Self> {
        let data = problems::table.find(name).first(&context.database)?;
        Ok(Self::new(context, data)?)
    }

    /// Get all the problems data in the database
    pub fn all(context: &'a ApiContext<'a>) -> FieldResult<Vec<Self>> {
        Ok(problems::table
            .load::<ProblemData>(&context.database)?
            .into_iter()
            .map(|data| Self::new(context, data))
            .collect::<Result<Vec<_>, _>>()?)
    }

    /// Insert a problem in the database
    pub fn insert(context: &ApiContext, inputs: Vec<ProblemInput>) -> FieldResult<()> {
        diesel::insert_into(problems::table)
            .values(inputs)
            .execute(&context.database)?;
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
                .set(&input)
                .execute(&context.database)?;
        }
        Ok(())
    }

    pub fn unpack(&self) -> PathBuf {
        Self::unpack_data(&self.data, &self.context)
    }

    fn unpack_data(data: &ProblemData, context: &ApiContext) -> PathBuf {
        context.unpack_archive(&data.archive_content.0, "problem")
    }

    /// Material of this problem
    fn get_problem_material(data: &ProblemData, context: &ApiContext) -> FieldResult<Material> {
        Ok(task_maker::generate_material(Self::unpack_data(
            data, context,
        ))?)
    }
}

/// A problem in the contest as seen by contestants
pub struct ProblemView<'a> {
    contest_view: &'a ContestView<'a>,
    problem: Problem<'a>,
}

/// A problem in a contest
#[juniper_ext::graphql]
#[allow(dead_code)]
impl ProblemView<'_> {
    /// Name of this problem. Unique in the current contest.
    fn name(&self) -> ProblemName {
        self.problem.name()
    }

    /// Material of this problem
    fn material(&self) -> &Material {
        self.problem.material()
    }

    /// Material of this problem
    fn tackling(&self) -> Option<ProblemTackling> {
        if self.contest_view.user_id().is_some() {
            Some(ProblemTackling { problem: &self })
        } else {
            None
        }
    }
}

impl<'a> ProblemView<'a> {
    pub fn by_name(contest_view: &'a ContestView<'a>, name: &str) -> FieldResult<Self> {
        let problem = Problem::by_name(contest_view.context(), name)?;
        Ok(ProblemView {
            contest_view,
            problem,
        })
    }

    /// Get all the problems data in the database
    pub fn all(contest_view: &'a ContestView<'a>) -> FieldResult<Vec<Self>> {
        let problems = Problem::all(contest_view.context())?;
        Ok(problems
            .into_iter()
            .map(|problem| ProblemView {
                contest_view,
                problem,
            })
            .collect())
    }
}

/// Attempts at solving a problem by a user in the contest
pub struct ProblemTackling<'a> {
    /// The problem
    problem: &'a ProblemView<'a>,
}

impl ProblemTackling<'_> {
    fn user_id(&self) -> UserId {
        self.problem.contest_view.user_id().clone().unwrap()
    }

    fn name(&self) -> String {
        self.problem.name().0
    }
}

/// Attempts at solving a problem by a user in the contest
#[juniper_ext::graphql]
#[allow(dead_code)]
impl ProblemTackling<'_> {
    /// Score awards of the current user (if to be shown)
    fn awards(&self) -> FieldResult<Vec<AwardOutcome>> {
        Ok(AwardOutcome::by_user_and_problem(
            &self.problem.contest_view.context(),
            &self.user_id().0,
            &self.name(),
        )?)
    }

    /// Submissions of the current user (if to be shown)
    fn submissions(&self) -> FieldResult<Vec<contest_submission::Submission>> {
        Ok(contest_submission::Submission::by_user_and_problem(
            &self.problem.contest_view.context(),
            &self.user_id().0,
            &self.name(),
        )?)
    }

    /// Indicates if the user can submit to this problem
    fn can_submit(&self) -> bool {
        true
    }
}
