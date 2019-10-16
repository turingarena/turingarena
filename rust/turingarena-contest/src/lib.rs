#![feature(decl_macro, proc_macro_hygiene)]

#[macro_use]
extern crate diesel;
extern crate juniper;
extern crate juniper_rocket;
extern crate rand;
extern crate rocket;

#[macro_use]
extern crate structopt;

use diesel::prelude::*;

pub mod contest;
pub mod problem;
pub mod submission;
pub mod user;
pub mod server;

pub struct Context {}
impl juniper::Context for Context {}

impl Context {
    fn connect_db(&self) -> ConnectionResult<SqliteConnection> {
        SqliteConnection::establish("./test.sqlite")
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
