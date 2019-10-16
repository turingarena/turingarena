#![doc(include = "README.md")]

extern crate juniper;

pub mod table;

use serde::{Deserialize, Serialize};

/// A feedback template, consisting of a list of sections.
/// The template can be rendered to users before evaluation,
/// and gradually filled with data coming from the evaluation.
pub type Template = Vec<Section>;

/// A section in the feedback template.
#[derive(Serialize, Deserialize, Clone)]
pub enum Section {
    /// A section containing tabular data.
    Table {
        /// Caption of this table. Roughly corresponding to `<caption>` HTML tag.
        caption: crate::content::Text,
        /// Columns of this table.
        cols: Vec<table::Col>,
        /// Row groupd of this table.
        row_groups: Vec<table::RowGroup>,
    },
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
