#![doc(include = "README.md")]

use super::{content::*, score};
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Clone)]
pub enum Section {
    Table {
        col_groups: Vec<table::ColGroup>,
        row_groups: Vec<table::RowGroup>,
        cells: Vec<table::Cell>,
    },
}

pub mod table {
    use super::*;

    #[derive(Serialize, Deserialize, Clone)]
    pub struct ColGroupId(pub String);
    #[derive(Serialize, Deserialize, Clone)]
    pub struct ColLocalId(pub String);
    #[derive(Serialize, Deserialize, Clone)]
    pub struct ColId(pub ColGroupId, pub ColLocalId);
    #[derive(Serialize, Deserialize, Clone)]
    pub struct RowGroupId(pub String);
    #[derive(Serialize, Deserialize, Clone)]
    pub struct RowLocalId(pub String);
    #[derive(Serialize, Deserialize, Clone)]
    pub struct RowId(pub RowGroupId, pub RowLocalId);

    #[derive(Serialize, Deserialize, Clone)]
    pub enum ColScope {
        Table,
        Group(ColGroupId),
        Col(ColId),
    }

    #[derive(Serialize, Deserialize, Clone)]
    pub enum RowScope {
        Table,
        Group(RowGroupId),
        Row(RowId),
    }

    #[derive(Serialize, Deserialize, Clone)]
    pub struct CellScope {
        pub row: RowScope,
        pub col: ColScope,
    }

    #[derive(Serialize, Deserialize, Clone)]
    pub struct ColGroup {
        pub id: ColGroupId,
        pub cols: Vec<Col>,
    }

    #[derive(Serialize, Deserialize, Clone)]
    pub struct Col {
        pub id: ColLocalId,
        pub def: def::ColDef,
    }

    #[derive(Serialize, Deserialize, Clone)]
    pub struct RowGroup {
        pub id: RowGroupId,
        pub rows: Vec<Row>,
    }

    #[derive(Serialize, Deserialize, Clone)]
    pub struct Row {
        pub id: RowLocalId,
        pub def: def::RowDef,
    }

    #[derive(Serialize, Deserialize, Clone)]
    pub struct Cell {
        pub scope: CellScope,
        pub def: def::CellDef,
    }

    mod def {
        use super::*;

        #[derive(Serialize, Deserialize, Clone)]
        pub enum ColDef {
            RowTitle,
            RowIndex,
            Score { range: score::Range },
        }

        #[derive(Serialize, Deserialize, Clone)]
        pub enum RowDef {
            Header,
            Footer,
            Data,
        }

        #[derive(Serialize, Deserialize, Clone)]
        pub enum CellDef {
            Title { value: Text },
            Index { value: u64 },
            Score {},
        }
    }
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
