#![doc(include = "README.md")]

extern crate juniper;

use super::content::*;
use serde::{Deserialize, Serialize};

/// Wraps a number that represents a score
#[derive(Serialize, Deserialize, Copy, Clone, juniper::GraphQLScalarValue)]
pub struct Score(pub f64);

/// Describes the possible values of a score.
#[derive(Serialize, Deserialize, Copy, Clone, juniper::GraphQLObject)]
pub struct Range {
    /// Number of significant decimal places.
    // FIXME: should be u8, but it is not trivially supported by juniper
    pub precision: i32,
    /// Maximum score.
    pub max: Score,
}

/// Describes an item to which a score can be assigned
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct ScoredItem {
    /// Name of this scored item, as shown to users.
    pub title: Text,
    /// Possible values for the score assigned to this item.
    pub range: Range,
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
