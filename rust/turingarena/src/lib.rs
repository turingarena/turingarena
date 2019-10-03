mod autoio;
mod batch;
mod bios;
mod content;
mod contest;
mod dce;
mod diff;
mod ev;
mod evr;
mod feedback;
mod make;
mod ppf;
mod ps;
mod rusage;
mod score;
mod submission;

#[macro_use]
extern crate derive_builder;

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
