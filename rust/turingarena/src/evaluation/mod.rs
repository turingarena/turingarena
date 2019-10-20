#![doc(include = "README.md")]

pub mod record;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub enum Event {
    Value {
        key: record::Key,
        value: record::Value,
    },
}

pub mod mem {
    use super::*;
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
