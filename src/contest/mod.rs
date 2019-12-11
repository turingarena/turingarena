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

#[cfg(feature = "cli-admin")]
pub mod cli_admin;

pub mod announcements;
pub mod api;
pub mod auth;
pub mod award;
pub mod contest;
pub mod contest_evaluation;
pub mod contest_problem;
pub mod formats;
pub mod questions;
pub mod schema;

#[cfg(feature = "server")]
pub mod server;

pub mod contest_submission;
pub mod graphql_schema;
pub mod user;

#[cfg(feature = "web")]
mod web_client;

/// Convenience Result type
pub type Result<T> = std::result::Result<T, Box<dyn std::error::Error>>;

use super::*;
