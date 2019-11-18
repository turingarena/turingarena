//! Securely run a program on a pre-defined input.
//!
//! Use to test solutions which do not require interactivity,
//! while limiting and/or measuring overall resource usage.
//!
//! Exposes a `turignarena::make` task type for convenience.

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
