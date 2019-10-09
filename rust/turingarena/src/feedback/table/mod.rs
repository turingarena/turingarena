#![doc(include = "README.md")]

use crate::{content::Text, evaluation::record::Key, score};
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Clone)]
pub struct Table {
    pub cols: Vec<Col>,
    pub row_groups: Vec<RowGroup>,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct Col {
    pub title: Text,
    pub content: ColContent,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct RowGroup {
    pub title: Text,
    pub rows: Vec<Row>,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct Row {
    pub content: RowContent,
    pub cells: Vec<Cell>,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct Cell {
    pub content: CellContent,
}

#[derive(Serialize, Deserialize, Clone)]
#[serde(rename_all = "snake_case")]
pub enum RowContent {
    Data,
}

#[derive(Serialize, Deserialize, Clone)]
#[serde(rename_all = "snake_case")]
pub enum ColContent {
    Title,
    Index,
    Score { range: score::Range },
}

#[derive(Serialize, Deserialize, Clone)]
#[serde(rename_all = "snake_case")]
pub enum CellContent {
    Missing,
    Title(Text),
    Index(u64),
    Score { range: score::Range, r#ref: Key },
}
