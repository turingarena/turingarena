//! Data-types for scores and awards.

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

impl ScoreRange {
    pub fn merge<I: IntoIterator<Item = Self>>(ranges: I) -> Self {
        ranges.into_iter().fold(
            Self {
                max: Score(0f64),
                allow_partial: true,
                precision: 0,
            },
            |a, b| Self {
                max: Score(a.max.0 + b.max.0),
                precision: std::cmp::max(a.precision, b.precision),
                ..a
            },
        )
    }
}

/// An award that has a numerical score
#[derive(Serialize, Deserialize, Copy, Clone, juniper::GraphQLObject)]
pub struct ScoreAwardDomain {
    pub range: ScoreRange,
}

/// An award that has only two possible states (success or fail)
#[derive(Serialize, Deserialize, Copy, Clone, GraphQLObjectFromUnit)]
pub struct BadgeAwardDomain;

/// Describes the nature of an award
#[derive(Serialize, Deserialize, Copy, Clone, GraphQLUnionFromEnum)]
pub enum AwardDomain {
    Score(ScoreAwardDomain),
    Badge(BadgeAwardDomain),
}

/// Describes an award
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct AwardMaterial {
    /// Name of this award, as shown to users.
    pub title: Text,
    /// Domain of values that can be won in this award.
    pub domain: AwardDomain,
}

/// Describes an award (i.e., score or badge) that can be won
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct Award {
    /// Name of this award, used to identify it.
    /// Should never be shown to (non-admin) users.
    pub name: AwardName,
    /// Material describing this award.
    pub material: AwardMaterial,
}

#[derive(Serialize, Deserialize, Clone, GraphQLUnionFromEnum)]
pub enum AwardValue {
    Score(ScoreAwardValue),
    Badge(BadgeAwardValue),
}

#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct ScoreAwardValue {
    pub score: Score,
}

#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct BadgeAwardValue {
    pub badge: bool,
}
