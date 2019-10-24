#![feature(decl_macro, proc_macro_hygiene)]

#[macro_use]
extern crate diesel;
#[macro_use]
extern crate diesel_migrations;
#[macro_use]
extern crate serde;
extern crate base64;
extern crate jsonwebtoken as jwt;
extern crate juniper;
extern crate juniper_rocket;
extern crate rand;
extern crate rocket;
extern crate serde_json;
extern crate structopt;
extern crate turingarena;
extern crate uuid;

#[cfg(test)]
extern crate tempdir;

mod auth;
mod contest;
mod evaluation;
mod problem;
mod schema;
mod server;
mod submission;
mod user;
mod args;

use diesel::prelude::*;
use args::Command;
use contest::Contest;
use server::{run_server, generate_schema};
use structopt::StructOpt;

embed_migrations!();

pub fn db_connect() -> ConnectionResult<SqliteConnection> {
    let url = std::env::var("DATABASE_URL").unwrap_or("./database.sqlite3".to_owned());
    SqliteConnection::establish(&url)
}

#[derive(Clone)]
pub struct Context {
    skip_auth: bool,
    secret: Vec<u8>,
    jwt_data: Option<auth::JwtData>,
}

impl Context {
    pub fn with_jwt_data(&self, jwt_data: Option<auth::JwtData>) -> Context {
        Context {
            jwt_data: jwt_data,
            ..self.clone()
        }
    }

    pub fn authorize_user(&self, user_id: &str) -> juniper::FieldResult<()> {
        if !self.skip_auth {
            if let Some(data) = &self.jwt_data {
                if data.user != user_id {
                    Err(juniper::FieldError::from("Forbidden for the given user id"))?
                }
            } else {
                Err(juniper::FieldError::from("Authentication required"))?
            }
        }
        Ok(())
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

pub type Schema = juniper::RootNode<'static, contest::Contest, contest::Contest>;

fn main() {
    use Command::*;
    match Command::from_args() {
        GenerateSchema {} => generate_schema(),
        Serve {
            host,
            port,
            secret_key,
            skip_auth,
        } => run_server(host, port, skip_auth, secret_key),
        InitDb {} => Contest::from_env().init_db(),
        AddUser {
            username,
            display_name,
            password,
        } => Contest::from_env().add_user(&username, &display_name, &password),
        DeleteUser { username } => Contest::from_env().delete_user(&username),
        AddProblem { name, path } => Contest::from_env().add_problem(&name, &path),
        DeleteProblem { name } => Contest::from_env().delete_problem(&name),
    }
}
