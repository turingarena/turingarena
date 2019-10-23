#![doc(include = "README.md")]

pub mod record;
use serde::{Deserialize, Serialize};

graphql_derive_union_from_enum! {
    #[derive(Serialize, Deserialize)]
    pub enum Event {
        Value(Value),
    }
}

/// Rappresents a key/value record type
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct Value {
    /// key of the record
    pub key: record::Key,

    /// value of the record
    pub value: record::Value,
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
