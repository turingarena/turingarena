#![doc(include = "README.md")]

use crate::{content::Text, evaluation::record::Key, score};
use serde::{Deserialize, Serialize};

/// A table column. Roughly corresponding to `<col>` HTML element.
#[derive(Serialize, Deserialize, Clone)]
pub struct Col {
    /// Name of this column, shown in a column header.
    pub title: Text,
    /// Kind of data shown in this column.
    pub content: ColContent,
}

/// A table row group. Roughly corresponding to `<tbody>` HTML element.
#[derive(Serialize, Deserialize, Clone)]
pub struct RowGroup {
    /// Name of this row group, shown in an header.
    pub title: Text,
    /// Rows in this group.
    pub rows: Vec<Row>,
}

/// A table row. Roughly corresponding to `<tr>` HTML element.
#[derive(Serialize, Deserialize, Clone)]
pub struct Row {
    /// Kind of data shown in this row.
    pub content: RowContent,
    /// Cells in this row.
    pub cells: Vec<Cell>,
}

/// A table cell. Roughly corresponding to either `<td>` or `<th>` HTML element.
#[derive(Serialize, Deserialize, Clone)]
pub struct Cell {
    /// Kind of data shown in this cell.
    /// Must be compatible with the kind of data of the corresponding row and column.
    pub content: CellContent,
}

/// Describes the kind of data shown in a row.
#[derive(Serialize, Deserialize, Clone)]
#[serde(rename_all = "snake_case")]
pub enum RowContent {
    /// Regular data.
    Data,
    /// Summary data for the whole row group.
    /// E.g., the total score, maximum resource usage, etc.
    GroupSummary,
}

/// Describes the kind of data shown in a column.
#[derive(Serialize, Deserialize, Clone)]
#[serde(rename_all = "snake_case")]
pub enum ColContent {
    /// Column of row titles.
    /// Cells must contain `CellContent::RowTitle`.
    RowTitle,
    /// Column of row numbers.
    /// Cells must contain `CellContent::RowNumber`.
    RowNumber,
    /// Column of scores.
    /// Cells must contain `CellContent::Score` or `CellContent::Missing`.
    Score {
        /// Score range that applies to all column cells.
        range: score::Range,
    },
}

/// Describes the kind of data shown in a cell.
#[derive(Serialize, Deserialize, Clone)]
#[serde(rename_all = "snake_case")]
pub enum CellContent {
    /// Cell containing no value.
    Missing,
    /// Cell containing the name of the corresponding row,
    /// shown as row header (e.g., using `<th scope=col>` elements).
    RowTitle(Text),
    /// Cell containing the number of the corresponding row,
    /// shown as row header (e.g., using `<th scope=col>` elements).
    RowNumber(u64),
    /// Cell containing a score.
    Score {
        /// Score range for this cell.
        /// Must be a sub-range of the column score range.
        range: score::Range,
        /// Reference to the evaluation value containing the score to show in this cell.
        r#ref: Key,
    },
}
