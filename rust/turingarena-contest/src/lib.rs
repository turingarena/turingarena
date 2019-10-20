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
extern crate structopt;
extern crate turingarena;
extern crate turingarena_contest_webcontent;
extern crate uuid;

#[cfg(test)]
extern crate tempdir;

use diesel::prelude::*;

pub mod auth;
pub mod contest;
pub mod evaluation;
pub mod problem;
pub mod schema;
pub mod server;
pub mod submission;
pub mod user;

embed_migrations!();

pub fn db_connect() -> ConnectionResult<SqliteConnection> {
    let url = std::env::var("DATABASE_URL").unwrap_or("./database.sqlite3".to_owned());
    SqliteConnection::establish(&url)
}

pub struct Context {
    jwt_data: Option<auth::JwtData>,
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
