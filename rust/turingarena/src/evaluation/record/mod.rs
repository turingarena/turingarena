#![doc(include = "README.md")]

extern crate juniper;

use serde::{Deserialize, Serialize};

use crate::{award, content, rusage};
use crate::feedback::valence::Valence;
use crate::juniper_ext::*;

/// Wraps a string used to identify a value of a given kind
#[derive(Serialize, Deserialize, Clone, GraphQLNewtype)]
pub struct Key(pub String);

#[derive(Serialize, Deserialize, Clone, GraphQLUnionFromEnum)]
pub enum Value {
    Message(TextValue),
    Score(ScoreValue),
    MemoryUsage(MemoryUsageValue),
    TimeUsage(TimeUsageValue),
    Valence(ValenceValue),
}

/// Wraps a Score
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct ScoreValue {
    /// The score
    pub score: award::Score,
}

/// Wraps a Text, that represents and evaluation message
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct TextValue {
    /// The message
    pub text: content::Text,
}

/// Wraps a MemoryUsage
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct MemoryUsageValue {
    /// The memory usage
    pub memory_usage: rusage::MemoryUsage,
}

/// Wraps a TimeUsage
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct TimeUsageValue {
    /// The time usage
    pub time_usage: rusage::TimeUsage,
}

/// Wraps a Valence
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct ValenceValue {
    /// The valence
    pub valence: Valence,
}
