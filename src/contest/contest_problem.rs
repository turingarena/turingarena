use super::*;

use super::contest::ContestView;
use crate::contest::award::AwardOutcome;
use api::ApiContext;
use award::*;
use diesel::{QueryDsl, QueryResult, RunQueryDsl, SqliteConnection};
use file::FileContentInput;
use juniper::{FieldError, FieldResult};
use problem::driver::ProblemDriver;
use problem::material::Material;
use problem::ProblemName;
use rand::Rng;
use schema::problems;
use std::path::PathBuf;
use user::UserId;

#[derive(Insertable)]
#[table_name = "problems"]
struct ProblemInsertable<'a> {
    name: &'a str,
    archive_content: &'a [u8],
}

#[derive(juniper::GraphQLInputObject)]
pub struct ProblemInput {
    name: String,
    archive_content: FileContentInput,
}

#[derive(Queryable, Clone, Debug)]
pub struct ProblemData {
    name: String,
    archive_content: Vec<u8>,
}

/// A problem in the contest
pub struct Problem<'a> {
    pub context: &'a ApiContext<'a>,
    /// Raw database data of the contest
    pub data: ProblemData,
}

/// A problem in a contest
#[juniper_ext::graphql]
impl Problem<'_> {
    /// Name of this problem. Unique in the current contest.
    fn name(&self) -> ProblemName {
        ProblemName(self.data.name.clone())
    }

    /// Material of this problem
    fn material(&self) -> FieldResult<Material> {
        self.get_problem_material().map_err(FieldError::from)
    }
}

impl Problem<'_> {
    /// Get a problem data by its name
    pub fn by_name<'a>(context: &'a ApiContext<'a>, name: &str) -> FieldResult<Problem<'a>> {
        let data = problems::table.find(name).first(&context.database)?;
        Ok(Problem { context, data })
    }

    /// Get all the problems data in the database
    pub fn all<'a>(context: &'a ApiContext<'a>) -> FieldResult<Vec<Problem>> {
        Ok(problems::table
            .load::<ProblemData>(&context.database)?
            .into_iter()
            .map(|data| Problem { context, data })
            .collect())
    }

    /// Insert a problem in the database
    pub fn insert<T: IntoIterator<Item = ProblemInput>>(
        context: &ApiContext,
        inputs: T,
    ) -> FieldResult<()> {
        for input in inputs.into_iter() {
            diesel::replace_into(problems::table)
                .values(ProblemInsertable {
                    name: &input.name,
                    archive_content: &input.archive_content.decode()?,
                })
                .execute(&context.database)?;
        }
        Ok(())
    }

    /// Delete a problem from the database
    pub fn delete(context: &ApiContext, name: ProblemName) -> FieldResult<()> {
        diesel::delete(problems::table.find(name.0)).execute(&context.database)?;
        Ok(())
    }

    pub fn unpack(&self) -> PathBuf {
        self.context
            .unpack_archive(&self.data.archive_content, "problem")
    }

    /// Material of this problem
    #[cfg(feature = "task-maker")]
    fn get_problem_material(&self) -> FieldResult<Material> {
        task_maker::driver::IoiProblemDriver::generate_material(self.unpack())
            .map_err(FieldError::from)
    }

    /// Material of this problem
    #[cfg(not(feature = "task-maker"))]
    fn get_problem_material(&self) -> FieldResult<Material> {
        unreachable!("Enable feature 'task-maker' to generate problem material")
    }
}

/// A problem in the contest as seen by contestants
pub struct ProblemView<'a> {
    pub contest_view: &'a ContestView<'a>,
    pub problem: Problem<'a>,
}

/// A problem in a contest
#[juniper_ext::graphql]
impl ProblemView<'_> {
    /// Name of this problem. Unique in the current contest.
    fn name(&self) -> ProblemName {
        self.problem.name()
    }

    /// Material of this problem
    fn material(&self) -> FieldResult<Material> {
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
    pub problem: &'a ProblemView<'a>,
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
