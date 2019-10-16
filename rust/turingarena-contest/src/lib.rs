#![feature(decl_macro, proc_macro_hygiene)]

#[macro_use]
extern crate diesel;
#[macro_use]
extern crate diesel_migrations;
extern crate juniper;
extern crate juniper_rocket;
extern crate rand;
extern crate rocket;
extern crate structopt;
extern crate turingarena_contest_webcontent;

use diesel::prelude::*;

pub mod contest;
pub mod problem;
pub mod submission;
pub mod user;
pub mod server;
pub mod schema;

embed_migrations!();

pub struct Context {}
impl juniper::Context for Context {}

pub fn connect_db() -> ConnectionResult<SqliteConnection> {
    let path = std::env::var("DATABASE_URL").unwrap_or("./database.sqlite3".to_owned());
    SqliteConnection::establish(&path)
}

pub fn init_db() {
    let connection = connect_db()
        .expect("Error connecting to the database");
    embedded_migrations::run_with_output(&connection, &mut std::io::stdout())
        .expect("Error while initializing the database");
}

impl Context {
    fn connect_db(&self) -> ConnectionResult<SqliteConnection> {
        connect_db()
    }
}

pub struct MutationOk;

#[juniper::object]
impl MutationOk {
    fn ok() -> bool {
        true
    }
}

pub type Schema = juniper::RootNode<'static, contest::Contest, contest::Contest>;
