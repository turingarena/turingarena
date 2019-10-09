#![doc(include = "README.md")]

pub mod table;

use serde::{Deserialize, Serialize};

pub type Template = Vec<Section>;

#[derive(Serialize, Deserialize, Clone)]
pub enum Section {
    Table(table::Table),
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
