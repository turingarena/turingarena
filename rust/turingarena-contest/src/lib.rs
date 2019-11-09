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

#[macro_use]
extern crate turingarena;

extern crate uuid;

#[cfg(feature = "web-content")]
extern crate turingarena_contest_web_content;

pub mod announcements;
pub mod auth;
pub mod config;
pub mod contest;
pub mod api;
pub mod evaluation;
pub mod formats;
pub mod problem;
pub mod questions;
pub mod schema;
pub mod server;
pub mod submission;
pub mod user;

/// Convenience Result type
pub type Result<T> = std::result::Result<T, Box<dyn std::error::Error>>;
