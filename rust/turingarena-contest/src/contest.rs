use juniper::{FieldError, FieldResult};

use crate::*;
use problem::*;
use schema::{problems, users};
use std::path::{Path, PathBuf};

#[derive(Clone)]
pub struct Contest {
    pub database_url: PathBuf,
    pub problems_dir: PathBuf,
}

/// a user authorization token
#[derive(juniper::GraphQLObject)]
pub struct UserToken {
    token: String,
}

type Result<T> = std::result::Result<T, Box<dyn std::error::Error>>;

impl Contest {
    pub fn problem_rel_path(&self, problem_path: &Path) -> Result<PathBuf> {
        let problems_abs = self.problems_dir.canonicalize()?;
        let problem_abs = problem_path.canonicalize()?;
        Ok(problem_abs.strip_prefix(problems_abs)?.to_owned())
    }

    pub fn connect_db(&self) -> ConnectionResult<SqliteConnection> {
        SqliteConnection::establish(self.database_url.to_str().unwrap())
    }

    pub fn init_db(&self) {
        let connection = self.connect_db().expect("Error connecting to the database");
        embedded_migrations::run_with_output(&connection, &mut std::io::stdout())
            .expect("Error while initializing the database");
    }

    pub fn add_user(&self, id: &str, display_name: &str, password: &str) {
        use crate::user::UserInput;
        let user = UserInput {
            id: id.to_owned(),
            display_name: display_name.to_owned(),
            password_bcrypt: bcrypt::hash(password, bcrypt::DEFAULT_COST).unwrap(),
        };
        let conn = self.connect_db().expect("cannot connect to database");
        diesel::insert_into(schema::users::table)
            .values(user)
            .execute(&conn)
            .expect("error executing user insert query");
    }

    pub fn delete_user(&self, id: &str) {
        use schema::users::dsl;
        let conn = self.connect_db().expect("cannot connect to database");
        diesel::delete(dsl::users.filter(dsl::id.eq(id)))
            .execute(&conn)
            .expect("error executing user delete query");
    }

    pub fn get_user(&self, id: &str) -> Result<user::User> {
        Ok(users::table.find(id).first(&self.connect_db()?)?)
    }

    pub fn add_problem(&self, name: &str, path: &Path) {
        let problem = ContestProblemInput {
            name: name.to_owned(),
            path: self
                .problem_rel_path(path)
                .unwrap()
                .to_str()
                .unwrap()
                .to_owned(),
        };
        let conn = self.connect_db().expect("cannot connect to database");
        diesel::insert_into(schema::problems::table)
            .values(problem)
            .execute(&conn)
            .expect("error executing problem insert query");
    }

    pub fn delete_problem(&self, name: &str) {
        use schema::problems::dsl;
        let conn = self.connect_db().expect("cannot connect to database");
        diesel::delete(dsl::problems.filter(dsl::name.eq(name)))
            .execute(&conn)
            .expect("error executing problem delete query");
    }

    pub fn get_problems(&self) -> Result<Vec<ContestProblem>> {
        Ok(problems::table.load::<ContestProblem>(&self.connect_db()?)?)
    }

    pub fn get_problem(&self, name: &str) -> Result<ContestProblem> {
        Ok(problems::table
            .find(name)
            .first::<ContestProblem>(&self.connect_db()?)?)
    }
}

/// dummy structure to do GraphQL queries to the contest
pub struct ContestQueries {}

#[juniper::object(Context = Context)]
impl ContestQueries {
    /// get a user
    fn user(&self, ctx: &Context, id: Option<String>) -> FieldResult<user::User> {
        let id = if let Some(id) = &id {
            id
        } else if let Some(ctx) = &ctx.jwt_data {
            &ctx.user
        } else {
            return Err(FieldError::from("invalid authorization token"));
        };
        Ok(ctx.contest.get_user(id)?)
    }

    /// list of problems in the contest
    fn problems(&self, ctx: &Context, context: &Context) -> FieldResult<Vec<ContestProblem>> {
        Ok(ctx.contest.get_problems()?)
    }

    /// get the evaluation events for the specified submission
    fn events(
        &self,
        ctx: &Context,
        submission_id: String,
    ) -> FieldResult<Vec<evaluation::EvaluationEvent>> {
        Ok(evaluation::query_events(
            &ctx.contest.connect_db()?,
            submission_id,
        )?)
    }
}

/// dummy structure to do GraphQL mutations to the contest
pub struct ContestMutations {}

#[juniper::object(Context = Context)]
impl ContestMutations {
    /// authenticate a user, generating an authentication code
    fn auth(&self, ctx: &Context, user: String, password: String) -> FieldResult<UserToken> {
        let user = ctx.contest.get_user(&user)?;
        Ok(UserToken {
            token: auth::auth(&user, &password, &ctx.secret)?,
        })
    }

    /// submit a solution to the specified problem
    fn submit(
        &self,
        ctx: &Context,
        user_id: String,
        problem_name: String,
        files: Vec<submission::FileInput>,
    ) -> FieldResult<submission::Submission> {
        ctx.authorize_user(&user_id)?;
        let problem = ctx.contest.get_problem(&problem_name)?;
        let submission =
            submission::insert(&ctx.contest.connect_db()?, &user_id, &problem_name, files)?;
        evaluation::evaluate(&problem, &submission, ctx.contest.connect_db().unwrap());
        Ok(submission)
    }
}

// #[cfg(test)]
// mod tests {
//     use super::*;
//     #[test]
//     fn test_problem_rel_path() {
//         let contest = Contest {
//             database_url: PathBuf::from(""),
//             problems_dir: PathBuf::from("test/dir1"),
//         };
//         assert_eq!(contest.problem_rel_path(&PathBuf::from("test/dir1/problems/problem1")).unwrap(), PathBuf::from("problems/p1"));
//     }
// }
