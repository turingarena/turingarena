#![doc(include = "README.md")]

use crate::{content::Text, evaluation::record::Key, score};
use serde::{Deserialize, Serialize};

/// Feedback section ontaining tabular data.
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct TableSection {
    /// Caption of this table. Roughly corresponding to `<caption>` HTML tag.
    pub caption: Text,
    /// Columns of this table.
    pub cols: Vec<Col>,
    /// Row groups of this table.
    pub row_groups: Vec<RowGroup>,
}

/// A table column. Roughly corresponding to `<col>` HTML element.
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct Col {
    /// Name of this column, shown in a column header.
    pub title: Text,
    /// Kind of data shown in this column.
    pub content: ColContent,
}

/// A table row group. Roughly corresponding to `<tbody>` HTML element.
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct RowGroup {
    /// Name of this row group, shown in an header.
    pub title: Text,
    /// Rows in this group.
    pub rows: Vec<Row>,
}

/// A table row. Roughly corresponding to `<tr>` HTML element.
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct Row {
    /// Kind of data shown in this row.
    pub content: RowContent,
    /// Cells in this row.
    pub cells: Vec<Cell>,
}

/// A table cell. Roughly corresponding to either `<td>` or `<th>` HTML element.
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct Cell {
    /// Kind of data shown in this cell.
    /// Must be compatible with the kind of data of the corresponding row and column.
    pub content: CellContent,
}

/// Describes the kind of data shown in a row.
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLEnum)]
#[serde(rename_all = "snake_case")]
pub enum RowContent {
    /// Regular data.
    Data,
    /// Summary data for the whole row group.
    /// E.g., the total score, maximum resource usage, etc.
    GroupSummary,
}

graphql_derive_union_from_enum! {
    /// Describes the kind of data shown in a column.
    #[derive(Serialize, Deserialize, Clone)]
    #[serde(rename_all = "snake_case")]
    pub enum ColContent {
        RowTitle(RowTitleColContent),
        RowNumber(RowNumberColContent),
        Score(ScoreColContent),
    }
}

/// Column of row titles.
/// Cells must contain `CellContent::RowTitle`.
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct RowTitleColContent {}

/// Column of row numbers.
/// Cells must contain `CellContent::RowNumber`.
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct RowNumberColContent {}

/// Column of scores.
/// Cells must contain `CellContent::Score` or `CellContent::Missing`.
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct ScoreColContent {
    /// Score range that applies to all column cells.
    pub range: score::Range,
}

graphql_derive_union_from_enum! {
    /// Describes the kind of data shown in a cell.
    #[derive(Serialize, Deserialize, Clone)]
    #[serde(rename_all = "snake_case")]
    pub enum CellContent {
        Missing(MissingCellContent),
        RowTitle(RowTitleCellContent),
        RowNumber(RowNumberCellContent),
        Score(ScoreCellContent),
    }
}

/// Cell containing no value.
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct MissingCellContent {}

/// Cell containing the name of the corresponding row,
/// shown as row header (e.g., using `<th scope=col>` elements).
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct RowTitleCellContent {
    pub title: Text,
}

/// Cell containing the number of the corresponding row,
/// shown as row header (e.g., using `<th scope=col>` elements).
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct RowNumberCellContent {
    pub number: i32,
}

/// Cell containing a score.
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct ScoreCellContent {
    /// Score range for this cell.
    /// Must be a sub-range of the column score range.
    pub range: score::Range,
    /// Reference to the evaluation value containing the score to show in this cell.
    pub r#ref: Key,
}
