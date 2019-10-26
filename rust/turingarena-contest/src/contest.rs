use juniper::{FieldError, FieldResult};

use crate::*;
use std::path::{Path, PathBuf};
use turingarena::problem::ProblemName;
use user::UserId;

#[derive(Clone)]
pub struct Contest {
    pub database_url: PathBuf,
    pub problems_dir: PathBuf,
}

/// A user authorization token
#[derive(juniper::GraphQLObject)]
pub struct UserToken {
    /// The user token encoded as a JWT
    pub token: String,
}

type Result<T> = std::result::Result<T, Box<dyn std::error::Error>>;

impl Contest {
    pub fn problem_rel_path(&self, problem_path: &Path) -> Result<PathBuf> {
        let problems_abs = self.problems_dir.canonicalize()?;
        let problem_abs = problem_path.canonicalize()?;
        Ok(problem_abs.strip_prefix(problems_abs)?.to_owned())
    }

    pub fn connect_db(&self) -> ConnectionResult<SqliteConnection> {
        let conn = SqliteConnection::establish(self.database_url.to_str().unwrap())?;
        conn.execute("PRAGMA busy_timeout = 5000;")
            .expect("Unable to set `busy_timeout`");
        Ok(conn)
    }

    pub fn init_db(&self, contest_title: &str) {
        let connection = self.connect_db().expect("Error connecting to the database");
        embedded_migrations::run_with_output(&connection, &mut std::io::stdout())
            .expect("Error while initializing the database");
        config::create_config(&connection, contest_title)
            .expect("Error creating contest configuration in the DB");
    }

    pub fn add_user(&self, id: &str, display_name: &str, token: &str) {
        let conn = self.connect_db().expect("cannot connect to database");
        user::insert(&conn, UserId(id.to_owned()), display_name, token)
            .expect("Error inserting user into the db");
    }

    pub fn delete_user(&self, id: &str) {
        let conn = self.connect_db().expect("cannot connect to database");
        user::delete(&conn, UserId(id.to_owned())).expect("Error deleting user from db");
    }

    pub fn add_problem(&self, name: &str, path: &Path) {
        let conn = self.connect_db().expect("cannot connect to database");
        let rel_path = self
            .problem_rel_path(path)
            .expect("Problem path is not valid");
        problem::insert(&conn, ProblemName(name.to_owned()), &rel_path)
            .expect("Error inserting the problem into the db")
    }

    pub fn delete_problem(&self, name: &str) {
        let conn = self.connect_db().expect("cannot connect to database");
        problem::delete(&conn, ProblemName(name.to_owned()))
            .expect("Error deleting problem from the db");
    }
}

/// dummy structure to do GraphQL queries to the contest
pub struct ContestQueries {}

#[juniper::object(Context = Context)]
impl ContestQueries {
    /// Get a user
    fn user(&self, ctx: &Context, id: Option<String>) -> FieldResult<user::User> {
        let id = if let Some(id) = &id {
            id
        } else if let Some(ctx) = &ctx.jwt_data {
            &ctx.user
        } else {
            return Err(FieldError::from("invalid authorization token"));
        };
        let user_id = user::UserId(id.to_owned());
        Ok(user::by_id(&ctx.contest.connect_db()?, user_id)?)
    }

    /// Get the submission with the specified id
    fn submission(
        &self,
        ctx: &Context,
        submission_id: String,
    ) -> FieldResult<submission::Submission> {
        // TODO: check privilage
        Ok(submission::query(
            &ctx.contest.connect_db()?,
            &submission_id,
        )?)
    }

    /// Authenticate a user, generating a JWT authentication token
    fn auth(&self, ctx: &Context, token: String) -> FieldResult<Option<UserToken>> {
        Ok(auth::auth(&ctx.contest.connect_db()?, &token, &ctx.secret)?)
    }

    /// Current time on the server as RFC3339 date
    fn server_time(&self) -> String {
        chrono::Local::now().to_rfc3339()
    }
}
