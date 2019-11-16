#![warn()]

extern crate base64;
extern crate jsonwebtoken as jwt;
extern crate juniper;
extern crate rand;
extern crate serde_json;
extern crate serde_yaml;
extern crate structopt;
#[cfg(test)]
extern crate tempdir;


extern crate uuid;

#[cfg(feature = "web-content")]
extern crate turingarena_contest_web_content;

#[cfg(feature = "cli-admin")]
pub mod cli_admin;

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

#[cfg(feature = "server")]
pub mod server;

pub mod submission;
pub mod user;
pub mod graphql_schema;

/// Convenience Result type
pub type Result<T> = std::result::Result<T, Box<dyn std::error::Error>>;
