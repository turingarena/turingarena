use crate::{auth, contest, problem, user, Result};
use auth::JwtData;
use chrono::{DateTime, Local};
use diesel::{Connection, ConnectionResult, SqliteConnection};
use std::path::PathBuf;
use turingarena::problem::ProblemName;
use user::UserId;
use std::default::Default;

embed_migrations!();

/// Context for the API
#[derive(Debug, Clone)]
pub struct Context {
    /// Skip all authentication
    skip_auth: bool,

    /// Secret code to use for authenticating a JWT token.
    pub secret: Option<Vec<u8>>,

    /// JWT data of the token submitted to the server (if any)
    jwt_data: Option<JwtData>,

    /// Path of the database on the filesystem
    pub database_url: PathBuf,

    /// Path of the problems directory on the filesystem
    pub problems_dir: PathBuf,
}

impl Default for Context {
    fn default() -> Context {
        Context {
            skip_auth: false,
            secret: None,
            jwt_data: None,
            database_url: PathBuf::default(),
            problems_dir: PathBuf::default(),
        }
    }
}

impl Context {
    /// Set the database URL
    pub fn with_database_url(self, database_url: PathBuf) -> Context {
        Context {
            database_url,
            ..self
        }
    }

    /// Set the problems directory
    pub fn with_problems_dir(self, problems_dir: PathBuf) -> Context {
        Context {
            problems_dir,
            ..self
        }
    }

    /// Sets a JWT data
    pub fn with_jwt_data(self, jwt_data: Option<JwtData>) -> Context {
        Context { jwt_data, ..self }
    }

    /// Sets a secret
    pub fn with_secret(self, secret: Option<Vec<u8>>) -> Context {
        Context { secret, ..self }
    }

    /// Sets if to skip authentication
    pub fn with_skip_auth(self, skip_auth: bool) -> Context {
        Context { skip_auth, ..self }
    }

    /// Authenticate user
    pub fn authorize_user(&self, user_id: &Option<UserId>) -> juniper::FieldResult<()> {
        if self.skip_auth {
            return Ok(());
        }

        if let Some(id) = user_id {
            if self.secret != None {
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

    /// Open a connection to the database
    pub fn connect_db(&self) -> ConnectionResult<SqliteConnection> {
        let conn = SqliteConnection::establish(self.database_url.to_str().unwrap())?;
        conn.execute("PRAGMA busy_timeout = 5000;")
            .expect("Unable to set `busy_timeout`");
        Ok(conn)
    }

    // TODO: move the following methods in a more appropriate location

    /// Initialize the database
    pub fn init_db(&self, contest_title: &str) -> Result<()> {
        embedded_migrations::run_with_output(&self.connect_db()?, &mut std::io::stdout())?;
        contest::create_config(&self.connect_db()?, contest_title)?;
        Ok(())
    }

    /// Add a user to the current contest
    pub fn add_user(&self, id: &str, display_name: &str, token: &str) -> Result<()> {
        user::insert(
            &self.connect_db()?,
            UserId(id.to_owned()),
            display_name,
            token,
        )?;
        Ok(())
    }

    /// Delete a user from the current contest
    pub fn delete_user(&self, id: &str) -> Result<()> {
        user::delete(&self.connect_db()?, UserId(id.to_owned()))?;
        Ok(())
    }

    /// Add a problem to the current contest
    pub fn add_problem(&self, name: &str) -> Result<()> {
        problem::insert(&self.connect_db()?, ProblemName(name.to_owned()))?;
        Ok(())
    }

    /// Delete a problem from the current contest
    pub fn delete_problem(&self, name: &str) -> Result<()> {
        problem::delete(&self.connect_db()?, ProblemName(name.to_owned()))?;
        Ok(())
    }

    /// Set the start time of the current contest
    pub fn set_start_time(&self, time: DateTime<Local>) -> Result<()> {
        contest::set_start_time(&self.connect_db()?, time)?;
        Ok(())
    }

    /// Set the end time of the current contest
    pub fn set_end_time(&self, time: DateTime<Local>) -> Result<()> {
        contest::set_end_time(&self.connect_db()?, time)?;
        Ok(())
    }
}

impl juniper::Context for Context {}
