#![feature(decl_macro, proc_macro_hygiene)]

#[macro_use]
extern crate diesel;
#[macro_use]
extern crate diesel_migrations;
#[macro_use]
extern crate serde;
extern crate juniper;
extern crate juniper_rocket;
extern crate rand;
extern crate rocket;
extern crate structopt;
extern crate turingarena;
extern crate turingarena_contest_webcontent;
extern crate jsonwebtoken as jwt;

use diesel::prelude::*;

pub mod contest;
pub mod problem;
pub mod submission;
pub mod user;
pub mod server;
pub mod schema;
pub mod auth;

embed_migrations!();


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
