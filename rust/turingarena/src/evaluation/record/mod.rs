#![doc(include = "README.md")]

use crate::{content, score};
use serde::{Deserialize, Serialize};

/// Wraps a string used to identify a value of a given kind
#[derive(Serialize, Deserialize, Clone)]
pub struct Key(pub String);

#[derive(Serialize, Deserialize, Clone)]
pub enum Kind {
    Message,
    Score,
}

#[derive(Serialize, Deserialize, Clone)]
pub enum Value {
    Message(content::Text),
    Score(score::Score),
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
