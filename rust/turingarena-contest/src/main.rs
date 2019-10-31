#![feature(decl_macro, proc_macro_hygiene)]
#![warn()]

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
extern crate serde_yaml;
extern crate structopt;
#[cfg(test)]
extern crate tempdir;
extern crate turingarena;
extern crate uuid;

#[cfg(feature = "web-content")]
extern crate turingarena_contest_web_content;

mod announcements;
mod args;
mod auth;
mod config;
mod contest;
mod context;
mod evaluation;
mod formats;
mod problem;
mod questions;
mod schema;
mod server;
mod submission;
mod user;

/// Convenience Result type
pub type Result<T> = std::result::Result<T, Box<dyn std::error::Error>>;

pub struct MutationOk;

#[juniper::object]
impl MutationOk {
    fn ok() -> bool {
        true
    }
}

pub type Schema = juniper::RootNode<'static, contest::ContestQueries, contest::ContestQueries>;

fn main() -> Result<()> {
    use args::{Args, Command::*};
    use context::Context;
    use server::{generate_schema, run_server};
    use structopt::StructOpt;

    let args = Args::from_args();
    let context = Context::default()
        .with_database_url(args.database_url)
        .with_problems_dir(args.problems_dir);
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
                return Err("Secret not provided".to_owned().into());
            }
            run_server(
                host,
                port,
                context
                    .with_skip_auth(skip_auth)
                    .with_secret(secret_key.map(|s| s.as_bytes().to_owned())),
            )
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
        ImportContest {
            path,
            format,
            force,
        } => {
            if force {
                std::fs::remove_file(&context.database_url)?;
            }
            formats::import(&context, &path, &format)
        }
    }
}
