use super::*;

extern crate turingarena;
extern crate turingarena_task_maker;

use juniper::{FieldError, FieldResult};
use schema::problems;
use turingarena::problem::driver::{ProblemDriver, ProblemPack};
use turingarena::problem::material::Material;
use turingarena::problem::ProblemName;
use user::UserId;

#[derive(Insertable)]
#[table_name = "problems"]
struct ProblemDataInput<'a> {
    name: &'a str,
}

#[derive(Queryable)]
pub struct ProblemData {
    name: String,
}

/// A problem in the contest
pub struct Problem {
    /// Raw database data of the contest
    pub data: ProblemData,

    /// Id of the user (if specified)
    pub user_id: Option<UserId>,
}

/// A problem in a contest
#[juniper::object(Context = Context)]
impl Problem {
    /// Name of this problem. Unique in the current contest.
    fn name(&self) -> ProblemName {
        ProblemName(self.data.name.clone())
    }

    /// Material of this problem
    fn material(&self, ctx: &Context) -> FieldResult<Material> {
        turingarena_task_maker::driver::IoiProblemDriver::gen_material(self.pack(ctx))
            .map_err(|e| FieldError::from(e))
    }

    /// Scorables of the current user (if to be shown)
    fn scores(&self, ctx: &Context) -> FieldResult<Option<Vec<evaluation::MaxScore>>> {
        let result = if let Some(UserId(user_id)) = &self.user_id {
            Some(evaluation::query_scorables_of_user_and_problem(
                &ctx.connect_db()?,
                &user_id,
                &self.data.name,
            )?)
        } else {
            None
        };
        Ok(result)
    }

    /// Submissions of the current user (if to be shown)
    fn submissions(&self, ctx: &Context) -> FieldResult<Option<Vec<submission::Submission>>> {
        let result = if let Some(UserId(user_id)) = &self.user_id {
            Some(submission::of_user_and_problem(
                &ctx.connect_db()?,
                &user_id,
                &self.data.name,
            )?)
        } else {
            None
        };
        Ok(result)
    }

    /// Submit a solution to the problem
    fn submit(
        &self,
        ctx: &Context,
        files: Vec<submission::FileInput>,
    ) -> FieldResult<submission::Submission> {
        if let Some(UserId(user_id)) = &self.user_id {
            let submission =
                submission::insert(&ctx.connect_db()?, &user_id, &self.data.name, files)?;
            evaluation::evaluate(self.pack(ctx), &submission, ctx.connect_db()?)?;
            Ok(submission)
        } else {
            Err(FieldError::from("Must specify a user id"))
        }
    }
}

impl Problem {
    /// Path of the problem
    fn path(&self, ctx: &Context) -> PathBuf {
        ctx.problems_dir.join(&self.data.name)
    }

    /// return the problem pack object
    fn pack(&self, ctx: &Context) -> ProblemPack {
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
    let problem = ProblemDataInput {
        name: &name.0,
    };
    diesel::insert_into(schema::problems::table)
        .values(problem)
        .execute(conn)?;
    Ok(())
}

/// Delete a problem from the database
pub fn delete(conn: &SqliteConnection, name: ProblemName) -> QueryResult<()> {
    diesel::delete(problems::table.find(name.0)).execute(conn)?;
    Ok(())
}
