#![feature(decl_macro, proc_macro_hygiene)]

#[macro_use]
extern crate diesel;

#[macro_use]
extern crate diesel_migrations;

#[macro_use]
extern crate serde;

#[macro_use]
extern crate turingarena;

mod contest;

pub use contest::*;
