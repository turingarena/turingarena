#![doc(include = "README.md")]

extern crate serde;

use crate::problem::*;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Clone)]
pub struct ContestDefinition {
    pub problems: Vec<ProblemName>,
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
