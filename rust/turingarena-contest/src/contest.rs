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
        use crate::user::UserInput;
        let user = UserInput {
            id: id,
            display_name,
            token,
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
        let problem = ProblemDataInput {
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

    pub fn get_problems(&self) -> Result<Vec<ProblemData>> {
        Ok(problems::table.load::<ProblemData>(&self.connect_db()?)?)
    }

    pub fn get_problem(&self, name: &str) -> Result<ProblemData> {
        Ok(problems::table
            .find(name)
            .first::<ProblemData>(&self.connect_db()?)?)
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
        Ok(ctx.contest.get_user(id)?)
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

    /// Get the contest configuration
    fn config(&self, ctx: &Context) -> FieldResult<config::Config> {
        Ok(config::current_config(&ctx.contest.connect_db()?)?)
    }

    /// Authenticate a user, generating a JWT authentication token 
    fn auth(&self, ctx: &Context, token: String) -> FieldResult<Option<UserToken>> {
        Ok(auth::auth(&ctx.contest.connect_db()?, &token, &ctx.secret)?)
    }
}
