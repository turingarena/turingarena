use super::*;

use super::contest::ContestView;
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
#[derive(Clone)]
pub struct Problem<'a> {
    pub contest_view: &'a ContestView<'a>,

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

    /// Material of this problem
    fn tackling(&self) -> Option<ProblemTackling> {
        if self.contest_view.user_id.is_some() {
            Some(ProblemTackling { problem: &self })
        } else {
            None
        }
    }
}

impl Problem<'_> {
    pub fn unpack(&self) -> PathBuf {
        self.contest_view
            .context
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

/// Get a problem data by its name
pub fn by_name(conn: &SqliteConnection, name: ProblemName) -> QueryResult<ProblemData> {
    problems::table.find(name.0).first(conn)
}

/// Get all the problems data in the database
pub fn all(conn: &SqliteConnection) -> QueryResult<Vec<ProblemData>> {
    problems::table.load(conn)
}

/// Insert a problem in the database
pub fn insert<T: IntoIterator<Item = ProblemInput>>(
    conn: &SqliteConnection,
    inputs: T,
) -> juniper::FieldResult<()> {
    for input in inputs.into_iter() {
        diesel::replace_into(problems::table)
            .values(ProblemInsertable {
                name: &input.name,
                archive_content: &input.archive_content.decode()?,
            })
            .execute(conn)?;
    }
    Ok(())
}

/// Delete a problem from the database
pub fn delete(conn: &SqliteConnection, name: ProblemName) -> QueryResult<()> {
    diesel::delete(problems::table.find(name.0)).execute(conn)?;
    Ok(())
}

/// Attempts at solving a problem by a user in the contest
pub struct ProblemTackling<'a> {
    /// The problem
    pub problem: &'a Problem<'a>,
}

impl ProblemTackling<'_> {
    fn user_id(&self) -> UserId {
        self.problem.contest_view.user_id.clone().unwrap()
    }

    fn name(&self) -> &str {
        &self.problem.data.name
    }
}

/// Attempts at solving a problem by a user in the contest
#[juniper_ext::graphql]
impl ProblemTackling<'_> {
    /// Score awards of the current user (if to be shown)
    fn scores(&self) -> FieldResult<Vec<MaxScoreAward>> {
        Ok(query_awards_of_user_and_problem(
            &self.problem.contest_view.context.database,
            "SCORE",
            &self.user_id().0,
            self.name(),
        )?
        .into_iter()
        .map(|data| MaxScoreAward { data })
        .collect())
    }

    /// Badge awards of the current user (if to be shown)
    fn badges(&self) -> FieldResult<Vec<BestBadgeAward>> {
        Ok(query_awards_of_user_and_problem(
            &self.problem.contest_view.context.database,
            "BADGE",
            &self.user_id().0,
            self.name(),
        )?
        .into_iter()
        .map(|data| BestBadgeAward { data })
        .collect())
    }

    /// Submissions of the current user (if to be shown)
    fn submissions(&self) -> FieldResult<Vec<contest_submission::Submission>> {
        Ok(contest_submission::of_user_and_problem(
            &self.problem.contest_view.context.database,
            &self.user_id().0,
            self.name(),
        )?
        .into_iter()
        .map(|data| contest_submission::Submission {
            context: self.problem.contest_view.context,
            data,
        })
        .collect())
    }

    /// Indicates if the user can submit to this problem
    fn can_submit(&self) -> bool {
        true
    }
}
