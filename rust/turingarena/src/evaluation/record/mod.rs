#![doc(include = "README.md")]

extern crate juniper;

use crate::{content, score};
use serde::{Deserialize, Serialize};

/// Wraps a string used to identify a value of a given kind
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLScalarValue)]
pub struct Key(pub String);

#[derive(Serialize, Deserialize, Clone, juniper::GraphQLEnum)]
pub enum Kind {
    Message,
    Score,
}

graphql_derive_union_from_enum! {
    #[derive(Serialize, Deserialize, Clone)]
    pub enum Value {
        Message(TextValue),
        Score(ScoreValue),
    }
}

#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct ScoreValue {
    pub score: score::Score,
}

#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct TextValue {
    pub text: content::Text,
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
