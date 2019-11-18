//! Data-types for evaluations.
//!
//! Evaluations are streams of (JSON-serializable) evaluation events.

use crate::award;
use crate::juniper_ext::*;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, GraphQLUnionFromEnum)]
pub enum Event {
    Value(ValueEvent),
    Score(ScoreEvent),
    Badge(BadgeEvent),
}

/// Rappresents a key/value record type
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct ValueEvent {
    /// key of the record
    pub key: record::Key,

    /// value of the record
    pub value: record::Value,
}

/// Rappresents a key/value record type
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct ScoreEvent {
    /// key of the record
    pub award_name: award::AwardName,

    /// value of the record
    pub score: award::Score,
}

/// Rappresents a key/value record type
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct BadgeEvent {
    /// key of the record
    pub award_name: award::AwardName,

    /// value of the record
    pub badge: bool,
}

pub mod mem {
    pub use super::*;
    use std::sync::mpsc::Receiver;
    // FIXME: should we use futures (async) or std::sync (theaded) `Receiver`s?
    pub struct Evaluation(pub Receiver<Event>);
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
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
