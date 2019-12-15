//! Data-types for evaluations.
//!
//! Evaluations are streams of (JSON-serializable) evaluation events.

use crate::award;
use crate::juniper_ext::*;
use serde::{Deserialize, Serialize};
use std::sync::mpsc::Receiver;

// FIXME: should we use futures (async) or std::sync (theaded) `Receiver`s?
pub struct Evaluation(pub Receiver<Event>);

#[derive(Serialize, Deserialize, GraphQLUnionFromEnum)]
pub enum Event {
    Value(ValueEvent),
    Award(AwardEvent),
}

/// Event meaning that settles the value for a given key
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct ValueEvent {
    /// key of the record
    pub key: record::Key,

    /// value of the record
    pub value: record::Value,
}

/// Event meaning that an award is... awarded
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct AwardEvent {
    /// Name of the awarded... award
    pub award_name: award::AwardName,

    /// Awarded value
    pub value: award::AwardValue,
}

/// A library to manage evaluations records, i.e., collection of key-value pairs computed during evaluation.
pub mod record {
    extern crate juniper;

    use serde::{Deserialize, Serialize};

    use crate::feedback::valence::Valence;
    use crate::juniper_ext::*;
    use crate::{award, content, rusage};

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
}
