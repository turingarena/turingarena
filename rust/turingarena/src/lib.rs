#![feature(external_doc)]

pub mod autoio;
pub mod batch;
pub mod bios;
pub mod content;
pub mod contest;
pub mod dce;
pub mod diff;
pub mod evaluation;
pub mod feedback;
pub mod make;
pub mod problem;
pub mod ps;
pub mod rusage;
pub mod score;
pub mod submission;

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
