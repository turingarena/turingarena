#![feature(decl_macro, proc_macro_hygiene)]
#![feature(external_doc)]
#![doc(include = "../README.md")]

pub extern crate juniper;

extern crate turingarena_proc_macro;

#[cfg(feature = "diesel")]
#[macro_use]
extern crate diesel;

#[cfg(feature = "diesel_migrations")]
#[macro_use]
extern crate diesel_migrations;

#[macro_use]
extern crate serde;

#[macro_use]
pub mod juniper_ext;

#[macro_use]
extern crate log;

pub mod autoio;
pub mod award;
pub mod batch;
pub mod bios;
pub mod content;

#[cfg(feature = "contest")]
pub mod contest;

pub mod dce;
pub mod diff;
pub mod evaluation;
pub mod exitstatus;
pub mod feedback;
pub mod make;
pub mod problem;
pub mod rusage;
pub mod submission;

#[cfg(feature = "task-maker")]
pub mod task_maker;

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
