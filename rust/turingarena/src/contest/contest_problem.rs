use super::*;

use api::ApiContext;
use diesel::{QueryDsl, QueryResult, RunQueryDsl, SqliteConnection};
use juniper::{FieldError, FieldResult};
use schema::problems;
use std::path::PathBuf;
use problem::driver::{ProblemDriver, ProblemPack};
use problem::material::Material;
use problem::ProblemName;
use user::UserId;

#[derive(Insertable)]
#[table_name = "problems"]
struct ProblemDataInput<'a> {
    name: &'a str,
}

#[derive(Queryable, Clone)]
pub struct ProblemData {
    name: String,
}

/// A problem in the contest
#[derive(Clone)]
pub struct Problem {
    /// Raw database data of the contest
    pub data: ProblemData,

    /// Id of the user (if specified)
    pub user_id: Option<UserId>,
}

/// A problem in a contest
#[juniper::object(Context = ApiContext)]
impl Problem {
    /// Name of this problem. Unique in the current contest.
    fn name(&self) -> ProblemName {
        ProblemName(self.data.name.clone())
    }

    /// Material of this problem
    fn material(&self, ctx: &ApiContext) -> FieldResult<Material> {
        get_problem_material(self.pack(ctx)).map_err(FieldError::from)
    }

    /// Material of this problem
    fn tackling(&self, ctx: &ApiContext) -> Option<ProblemTackling> {
        if self.user_id.is_some() {
            Some(ProblemTackling { problem: Box::new((*self).clone()) })
        } else {
            None
        }
    }
}
/// Material of this problem
#[cfg(feature = "task-maker")]
fn get_problem_material(pack: ProblemPack) -> FieldResult<Material> {
    task_maker::driver::IoiProblemDriver::gen_material(pack)
        .map_err(FieldError::from)
}

/// Material of this problem
#[cfg(not(feature = "task-maker"))]
fn get_problem_material(pack: ProblemPack) -> FieldResult<Material> {
    unreachable!("Enable feature 'task-maker' to generate problem material")
}


impl Problem {
    /// Path of the problem
    pub fn path(&self, ctx: &ApiContext) -> PathBuf {
        ctx.problems_dir.join(&self.data.name)
    }

    /// return the problem pack object
    pub fn pack(&self, ctx: &ApiContext) -> ProblemPack {
        ProblemPack(std::path::PathBuf::from(&self.path(ctx)))
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
pub fn insert(conn: &SqliteConnection, name: ProblemName) -> QueryResult<()> {
    let problem = ProblemDataInput { name: &name.0 };
    // FIXME: replace_into not supported by PostgreSQL
    diesel::replace_into(schema::problems::table)
        .values(problem)
        .execute(conn)?;
    Ok(())
}

/// Delete a problem from the database
pub fn delete(conn: &SqliteConnection, name: ProblemName) -> QueryResult<()> {
    diesel::delete(problems::table.find(name.0)).execute(conn)?;
    Ok(())
}

/// Attempts at solving a problem by a user in the contest
pub struct ProblemTackling {
    /// The problem
    pub problem: Box<Problem>,
}

impl ProblemTackling {
    fn user_id(&self) -> UserId {
        self.problem.user_id.clone().unwrap()
    }

    fn name(&self) -> &str {
        &self.problem.data.name
    }
}

/// Attempts at solving a problem by a user in the contest
#[juniper::object(Context = ApiContext)]
impl ProblemTackling {
    /// Score awards of the current user (if to be shown)
    fn scores(&self, ctx: &ApiContext) -> FieldResult<Vec<contest_evaluation::MaxScoreAward>> {
        Ok(contest_evaluation::query_score_awards_of_user_and_problem(
            &ctx.connect_db()?,
            &self.user_id().0,
            self.name(),
        )?)
    }

    /// Badge awards of the current user (if to be shown)
    fn badges(&self, ctx: &ApiContext) -> FieldResult<Vec<contest_evaluation::BestBadgeAward>> {
        Ok(contest_evaluation::query_badge_awards_of_user_and_problem(
            &ctx.connect_db()?,
            &self.user_id().0,
            self.name(),
        )?)
    }

    /// Submissions of the current user (if to be shown)
    fn submissions(&self, ctx: &ApiContext) -> FieldResult<Vec<contest_submission::Submission>> {
        Ok(contest_submission::of_user_and_problem(
            &ctx.connect_db()?,
            &self.user_id().0,
            self.name(),
        )?)
    }

    /// Indicates if the user can submit to this problem
    fn can_submit(&self) -> bool {
        true
    }
}