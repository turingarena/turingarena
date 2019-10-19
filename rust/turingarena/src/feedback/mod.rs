#![doc(include = "README.md")]

extern crate juniper;

pub mod table;

use serde::{Deserialize, Serialize};
use table::TableSection;

/// A feedback template, consisting of a list of sections.
/// The template can be rendered to users before evaluation,
/// and gradually filled with data coming from the evaluation.
pub type Template = Vec<Section>;

graphql_derive_union_from_enum! {
    /// A section in the feedback template.
    #[derive(Serialize, Deserialize, Clone)]
    pub enum Section {
        /// A section containing tabular data.
        Table(TableSection),
    }
}

#[cfg(test)]

mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
