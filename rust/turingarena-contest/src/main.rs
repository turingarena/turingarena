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

#[cfg(feature = "webcontent")]
extern crate turingarena_contest_webcontent;

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

use args::{Args, Command};
use contest::Contest;
use diesel::prelude::*;
use server::{generate_schema, run_server};
use structopt::StructOpt;

embed_migrations!();

#[derive(Clone)]
pub struct Context {
    skip_auth: bool,
    secret: Vec<u8>,
    jwt_data: Option<auth::JwtData>,
    contest: Contest,
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

pub type Schema = juniper::RootNode<'static, contest::ContestQueries, contest::ContestMutations>;

fn main() {
    let args = Args::from_args();
    let contest = Contest {
        database_url: args.database_url.clone(),
        problems_dir: args.problems_dir.clone(),
    };
    use Command::*;
    match args.subcommand {
        GenerateSchema {} => generate_schema(),
        Serve {
            host,
            port,
            secret_key,
            skip_auth,
        } => run_server(host, port, skip_auth, secret_key, contest),
        InitDb { contest_title } => contest.init_db(&contest_title),
        AddUser {
            username,
            display_name,
            password,
        } => contest.add_user(&username, &display_name, &password),
        DeleteUser { username } => contest.delete_user(&username),
        AddProblem { name, path } => contest.add_problem(&name, &path),
        DeleteProblem { name } => contest.delete_problem(&name),
    }
}
