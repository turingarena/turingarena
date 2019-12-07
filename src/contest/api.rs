use std::default::Default;
use std::path::PathBuf;

use chrono::{DateTime, Local};
use diesel::{Connection, ConnectionResult, SqliteConnection};
use juniper::{FieldError, FieldResult};
use structopt::StructOpt;

use auth::JwtData;
use contest::{ContestView, UserToken};
use contest_problem::Problem;
use formats::{import, ImportInput};
use problem::ProblemName;
use user::UserId;
use user::UserInput;

use super::*;

embed_migrations!();

pub struct MutationOk;

#[juniper::object]
impl MutationOk {
    fn ok() -> bool {
        true
    }
}

pub type RootNode<'a> = juniper::RootNode<'static, Query<'a>, Mutation<'a>>;

#[derive(StructOpt, Debug)]
pub struct ContestArgs {
    /// url of the database
    #[structopt(long, env = "DATABASE_URL", default_value = "./database.sqlite3")]
    pub database_url: PathBuf,

    /// path of the directory in which are contained the problems
    #[structopt(long, env = "PROBLEMS_DIR", default_value = "./")]
    pub problems_dir: PathBuf,
}

#[derive(Debug, Clone)]
pub struct ApiConfig {
    /// Skip all authentication
    skip_auth: bool,

    /// Secret code to use for authenticating a JWT token.
    pub secret: Option<Vec<u8>>,

    /// Path of the database on the filesystem
    pub database_url: PathBuf,

    /// Path of the problems directory on the filesystem
    pub problems_dir: PathBuf,
}

pub struct ApiContext<'a> {
    pub config: &'a ApiConfig,
    /// JWT data of the token submitted to the server (if any)
    pub jwt_data: Option<JwtData>,
    pub database: SqliteConnection,
}

impl Default for ApiConfig {
    fn default() -> ApiConfig {
        ApiConfig {
            skip_auth: false,
            secret: None,
            database_url: PathBuf::default(),
            problems_dir: PathBuf::default(),
        }
    }
}

impl ApiConfig {
    pub fn create_context(&self, jwt_data: Option<JwtData>) -> ApiContext {
        ApiContext {
            config: &self,
            database: self.connect_db(),
            jwt_data,
        }
    }

    fn connect_db(&self) -> SqliteConnection {
        let conn = SqliteConnection::establish(self.database_url.to_str().unwrap())
            .expect("Unable to establish connection");
        conn.execute("PRAGMA busy_timeout = 5000;")
            .expect("Unable to set `busy_timeout`");
        conn
    }

    pub fn with_args(self, args: ContestArgs) -> ApiConfig {
        self.with_database_url(args.database_url)
            .with_problems_dir(args.problems_dir)
    }

    /// Set the database URL
    pub fn with_database_url(self, database_url: PathBuf) -> ApiConfig {
        ApiConfig {
            database_url,
            ..self
        }
    }

    /// Set the problems directory
    pub fn with_problems_dir(self, problems_dir: PathBuf) -> ApiConfig {
        ApiConfig {
            problems_dir,
            ..self
        }
    }

    /// Sets a secret
    pub fn with_secret(self, secret: Option<Vec<u8>>) -> ApiConfig {
        ApiConfig { secret, ..self }
    }

    /// Sets if to skip authentication
    pub fn with_skip_auth(self, skip_auth: bool) -> ApiConfig {
        ApiConfig { skip_auth, ..self }
    }
}

impl ApiContext<'_> {
    pub fn root_node(&self) -> RootNode {
        RootNode::new(Query { context: &self }, Mutation { context: &self })
    }

    /// Authorize admin operations
    pub fn authorize_admin(&self) -> juniper::FieldResult<()> {
        if self.config.skip_auth {
            return Ok(());
        }
        return Err(juniper::FieldError::from("Forbidden"));
    }

    /// Authenticate user
    pub fn authorize_user(&self, user_id: &Option<UserId>) -> juniper::FieldResult<()> {
        if self.config.skip_auth {
            return Ok(());
        }

        if let Some(id) = user_id {
            if self.config.secret != None {
                if let Some(data) = &self.jwt_data {
                    if data.user != id.0 {
                        return Err(juniper::FieldError::from("Forbidden for the given user id"));
                    }
                } else {
                    return Err(juniper::FieldError::from("Authentication required"));
                }
            }
        }
        Ok(())
    }

    // TODO: move the following methods in a more appropriate location

    /// Initialize the database
    pub fn init_db(&self) -> Result<()> {
        embedded_migrations::run_with_output(&self.database, &mut std::io::stdout())?;
        contest::create_config(&self.database)?;
        Ok(())
    }

    /// Set the start time of the current contest
    pub fn set_start_time(&self, time: DateTime<Local>) -> Result<()> {
        contest::set_start_time(&self.database, time)?;
        Ok(())
    }

    /// Set the end time of the current contest
    pub fn set_end_time(&self, time: DateTime<Local>) -> Result<()> {
        contest::set_end_time(&self.database, time)?;
        Ok(())
    }
}

pub struct Query<'a> {
    pub context: &'a ApiContext<'a>,
}

#[juniper_ext::graphql]
impl Query<'_> {
    /// Get the view of a contest
    fn contest_view(&self, user_id: Option<UserId>) -> FieldResult<ContestView> {
        self.context.authorize_user(&user_id)?;

        Ok(ContestView {
            context: self.context,
            user_id,
        })
    }

    /// Get the submission with the specified id
    fn submission(&self, submission_id: String) -> FieldResult<contest_submission::Submission> {
        // TODO: check privilage
        let data = contest_submission::query(&self.context.database, &submission_id)?;
        Ok(contest_submission::Submission {
            context: self.context,
            data,
        })
    }

    /// Current time on the server as RFC3339 date
    fn server_time(&self) -> String {
        chrono::Local::now().to_rfc3339()
    }
}

pub struct Mutation<'a> {
    pub context: &'a ApiContext<'a>,
}

#[juniper_ext::graphql]
impl Mutation<'_> {
    /// Reset database
    fn init_db(&self) -> FieldResult<MutationOk> {
        self.context.authorize_admin()?;
        self.context.init_db()?;
        Ok(MutationOk)
    }

    /// Authenticate a user, generating a JWT authentication token
    fn auth(&self, token: String) -> FieldResult<Option<UserToken>> {
        Ok(auth::auth(
            &self.context.database,
            &token,
            self.context
                .config
                .secret
                .as_ref()
                .ok_or_else(|| FieldError::from("Authentication disabled"))?,
        )?)
    }

    /// Current time on the server as RFC3339 date
    fn server_time() -> String {
        chrono::Local::now().to_rfc3339()
    }

    /// Add a user to the current contest
    pub fn add_user(&self, input: UserInput) -> FieldResult<MutationOk> {
        self.context.authorize_admin()?;

        user::insert(&self.context.database, &input)?;

        Ok(MutationOk)
    }

    /// Delete a user from the current contest
    pub fn delete_user(&self, id: String) -> FieldResult<MutationOk> {
        self.context.authorize_admin()?;

        user::delete(&self.context.database, UserId(id.to_owned()))?;

        Ok(MutationOk)
    }

    /// Add a problem to the current contest
    pub fn add_problem(&self, name: String) -> FieldResult<MutationOk> {
        contest_problem::insert(&self.context.database, ProblemName(name))?;
        Ok(MutationOk)
    }

    /// Delete a problem from the current contest
    pub fn delete_problem(&self, name: String) -> FieldResult<MutationOk> {
        contest_problem::delete(&self.context.database, ProblemName(name))?;
        Ok(MutationOk)
    }

    /// Import a file
    pub fn import(&self, input: ImportInput) -> FieldResult<MutationOk> {
        import(&self.context, &input)?;
        Ok(MutationOk)
    }

    /// Submit a solution to the problem
    fn submit(
        &self,
        user_id: UserId,
        problem_name: ProblemName,
        files: Vec<contest_submission::FileInput>,
    ) -> FieldResult<contest_submission::Submission> {
        let conn = &self.context.database;
        let data = contest_submission::insert(&conn, &user_id.0, &problem_name.0, files)?;
        let problem = Problem {
            data: contest_problem::by_name(&conn, problem_name)?,
            contest_view: &ContestView {
                context: self.context,
                user_id: Some(user_id),
            },
        };
        let submission = contest_submission::Submission {
            context: self.context,
            data: data.clone(),
        };
        contest_evaluation::evaluate(problem.pack(), &data, &self.context.config)?;
        Ok(submission)
    }
}
