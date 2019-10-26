#![doc(include = "README.md")]

pub mod record;
use crate::award;
use serde::{Deserialize, Serialize};

graphql_derive_union_from_enum! {
    #[derive(Serialize, Deserialize)]
    pub enum Event {
        Value(ValueEvent),
        Score(ScoreEvent),
        Badge(BadgeEvent),
    }
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
