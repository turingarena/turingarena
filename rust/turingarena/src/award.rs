//! Data-types for scorable items and scores.

extern crate juniper;

use super::content::*;
use super::juniper_ext::*;
use serde::{Deserialize, Serialize};

/// Wraps a number that represents a score
#[derive(Serialize, Deserialize, Copy, Clone, GraphQLNewtype)]
pub struct Score(pub f64);

/// Wraps a string that identifies an award
#[derive(Serialize, Deserialize, Clone, GraphQLNewtype)]
pub struct AwardName(pub String);

/// Describes the possible values of a score.
#[derive(Serialize, Deserialize, Copy, Clone, juniper::GraphQLObject)]
pub struct ScoreRange {
    /// Number of significant decimal places.
    // FIXME: should be u8, but it is not trivially supported by juniper
    pub precision: i32,
    /// Maximum score.
    pub max: Score,
    /// Whether partial scores are allowed. If `false`, score must be either zero or `max`.
    pub allow_partial: bool,
}

/// An award that has a numerical score
#[derive(Serialize, Deserialize, Copy, Clone, juniper::GraphQLObject)]
pub struct ScoreAwardContent {
    pub range: ScoreRange,
}

/// An award that has only two possible states (success or fail)
#[derive(Serialize, Deserialize, Copy, Clone, GraphQLObjectFromUnit)]
pub struct BadgeAwardContent;

/// Describes the nature of an award
#[derive(Serialize, Deserialize, Copy, Clone, GraphQLUnionFromEnum)]
pub enum AwardContent {
    Score(ScoreAwardContent),
    Badge(BadgeAwardContent),
}

/// Describes an item to which a score can be assigned
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct Award {
    /// Name of this award, used to identify it.
    /// Should never be shown to (non-admin) users.
    pub name: AwardName,
    /// Name of this award, as shown to users.
    pub title: Text,
    /// Content of this award.
    pub content: AwardContent,
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
