#![feature(external_doc)]
#![doc(include = "../README.md")]

pub mod autoio;
pub mod batch;
pub mod bios;
pub mod content;
pub mod dce;
pub mod diff;
pub mod evaluation;
pub mod exitstatus;
pub mod feedback;
pub mod make;
pub mod problem;
pub mod rusage;
pub mod score;
pub mod submission;

extern crate juniper;

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
