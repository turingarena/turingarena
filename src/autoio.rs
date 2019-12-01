//! Automation of generation/parsing of input/output streams.
//!
//! Used for automatic validation, documentation, and code generation.
//!
//! # Skeletons
//!
//! A format of I/O is expressed by defining a _skeleton_.
//!
//! A skeleton is a program which reads the input variables,
//! invokes user-defined functions,
//! and writes the output variables.
//! This skeleton is defined in abstract language,
//! it is analyzed statically,
//! and is used to generate concrete skeletons in various programming languages.

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
