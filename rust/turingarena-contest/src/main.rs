#![feature(decl_macro, proc_macro_hygiene)]

extern crate base64;
#[macro_use]
extern crate diesel;
#[macro_use]
extern crate diesel_migrations;
extern crate jsonwebtoken as jwt;
extern crate juniper;
extern crate juniper_rocket;
extern crate rand;
extern crate rocket;
#[macro_use]
extern crate serde;
extern crate serde_json;
extern crate structopt;
#[cfg(test)]
extern crate tempdir;
extern crate turingarena;
#[cfg(feature = "webcontent")]
extern crate turingarena_contest_webcontent;
extern crate uuid;

use std::default::Default;
use std::path::PathBuf;

use diesel::prelude::*;
use structopt::StructOpt;

use args::{Args, Command};
use server::{generate_schema, run_server};
use turingarena::problem::ProblemName;
use user::UserId;

mod args;
mod auth;
mod config;
mod contest;
mod evaluation;
mod problem;
mod schema;
mod server;
mod submission;
mod user;

embed_migrations!();

/// Context for the API
#[derive(Debug, Clone)]
pub struct Context {
    /// Skip all authentication
    skip_auth: bool,

    /// Secret code to use for authenticating a JWT token.
    secret: Option<Vec<u8>>,

    /// JWT data of the token submitted to the server (if any)
    jwt_data: Option<auth::JwtData>,

    /// Path of the database on the filesystem
    database_url: PathBuf,

    /// Path of the problems directory on the filesystem
    pub problems_dir: PathBuf,
}

impl Context {
    /// Create a new Context
    pub fn new() -> Context {
        Context {
            skip_auth: false,
            secret: None,
            jwt_data: None,
            database_url: PathBuf::default(),
            problems_dir: PathBuf::default(),
        }
    }

    /// Set the database URL
    pub fn with_database_url(self, database_url: PathBuf) -> Context {
        Context {
            database_url,
            ..self
        }
    }

    /// Set the problems directory
    fn with_problems_dir(self, problems_dir: PathBuf) -> Context {
        Context {
            problems_dir,
            ..self
        }
    }

    /// Sets a JWT data
    pub fn with_jwt_data(self, jwt_data: Option<auth::JwtData>) -> Context {
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
                        return Err(juniper::FieldError::from("Forbidden for the given user id"))
                    }
                } else {
                    return Err(juniper::FieldError::from("Authentication required"))
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
    fn init_db(&self, contest_title: &str) {
        let connection = self.connect_db().expect("Error connecting to the database");
        embedded_migrations::run_with_output(&connection, &mut std::io::stdout())
            .expect("Error while initializing the database");
        config::create_config(&connection, contest_title)
            .expect("Error creating contest configuration in the DB");
    }

    fn add_user(&self, id: &str, display_name: &str, token: &str) {
        let conn = self.connect_db().expect("cannot connect to database");
        user::insert(&conn, UserId(id.to_owned()), display_name, token)
            .expect("Error inserting user into the db");
    }

    fn delete_user(&self, id: &str) {
        let conn = self.connect_db().expect("cannot connect to database");
        user::delete(&conn, UserId(id.to_owned())).expect("Error deleting user from db");
    }

    fn add_problem(&self, name: &str) {
        let conn = self.connect_db().expect("cannot connect to database");
        problem::insert(&conn, ProblemName(name.to_owned()))
            .expect("Error inserting the problem into the db")
    }

    fn delete_problem(&self, name: &str) {
        let conn = self.connect_db().expect("cannot connect to database");
        problem::delete(&conn, ProblemName(name.to_owned()))
            .expect("Error deleting problem from the db");
    }
}

impl juniper::Context for Context {}

pub struct MutationOk;

#[juniper::object]
impl MutationOk {
    fn ok() -> bool {
        true
    }
}

pub type Schema = juniper::RootNode<'static, contest::ContestQueries, contest::ContestQueries>;

fn main() {
    let args = Args::from_args();
    let context = Context::new()
        .with_database_url(args.database_url)
        .with_problems_dir(args.problems_dir);
    use Command::*;
    match args.subcommand {
        GenerateSchema {} => generate_schema(context),
        Serve {
            host,
            port,
            secret_key,
            skip_auth,
        } => {
            if skip_auth {
                eprintln!("WARNING: authentication disabled");
            } else if secret_key == None {
                eprintln!("ERROR: provide a secret OR set skip-auth");
                return;
            }
            run_server(
                host,
                port,
                context
                    .with_skip_auth(skip_auth)
                    .with_secret(secret_key.map(|s| s.as_bytes().to_owned())),
            );
        }
        InitDb { contest_title } => context.init_db(&contest_title),
        AddUser {
            username,
            display_name,
            token,
        } => context.add_user(&username, &display_name, &token),
        DeleteUser { username } => context.delete_user(&username),
        AddProblem { name } => context.add_problem(&name),
        DeleteProblem { name } => context.delete_problem(&name),
    }
}
