#![feature(decl_macro, proc_macro_hygiene)]

#[macro_use]
extern crate diesel;

#[macro_use]
extern crate diesel_migrations;

#[macro_use]
extern crate serde;

#[macro_use]
pub mod juniper_ext;

#[macro_use]
extern crate log;

pub mod award;
pub mod content;
pub mod contest;
pub mod evallib;
pub mod evaluation;
pub mod exitstatus;
pub mod feedback;
pub mod file;
pub mod problem;
pub mod rusage;
pub mod submission;
pub mod task_maker;

pub mod archive;
