#![doc(include = "README.md")]

use serde::{Deserialize, Serialize};

use crate::{award, content::Text, evaluation::record::Key};
use crate::rusage::{MemoryUsage, TimeUsage};

/// Feedback section containing tabular data.
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
        Message(MessageColContent),
        TimeUsage(TimeUsageColContent),
        MemoryUsage(MemoryUsageColContent),
    }
}

graphql_derive_object_from_unit! {
    /// Column of row titles.
    /// Cells must contain `CellContent::RowTitle`.
    #[derive(Serialize, Deserialize, Clone)]
    pub struct RowTitleColContent;
}

graphql_derive_object_from_unit! {
    /// Column of row numbers.
    /// Cells must contain `CellContent::RowNumber`.
    #[derive(Serialize, Deserialize, Clone)]
    pub struct RowNumberColContent;
}

/// Column of scores.
/// Cells must contain `CellContent::Score` or `CellContent::Missing`.
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct ScoreColContent {
    /// Score range that applies to all column cells.
    pub range: award::ScoreRange,
}

graphql_derive_object_from_unit! {
    /// Column of text messages.
    /// Cells must contain `CellContent::Message` or `CellContent::Missing`.
    #[derive(Serialize, Deserialize, Clone)]
    pub struct MessageColContent;
}

graphql_derive_object_from_unit! {
    /// Column containing amounts of time used for computation.
    /// Cells must contain `CellContent::TimeUsage`.
    #[derive(Serialize, Deserialize, Clone)]
    pub struct TimeUsageColContent;
}

graphql_derive_object_from_unit! {
    /// Column containing amounts of memory used for computation.
    /// Cells must contain `CellContent::MemoryUsage`.
    #[derive(Serialize, Deserialize, Clone)]
    pub struct MemoryUsageColContent;
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
        Message(MessageCellContent),
        TimeUsage(TimeUsageCellContent),
        MemoryUsage(MemoryUsageCellContent),
    }
}

graphql_derive_object_from_unit! {
    /// Cell containing no value.
    #[derive(Serialize, Deserialize, Clone)]
    pub struct MissingCellContent;
}

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
    pub range: award::ScoreRange,
    /// Reference to the evaluation value containing the score to show in this cell.
    #[graphql(name = "ref")]
    pub r#ref: Key,
}

/// Cell containing an amount of time used for computation.
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct TimeUsageCellContent {
    /// Maximum time usage expected to be represented faithfully.
    /// Determines the scale of the representation (e.g., the units).
    pub max_relevant: TimeUsage,

    /// Time usage that should be presented as the main limit.
    pub primary_watermark: Option<TimeUsage>,

    // TODO: add secondary watermarks (each with a title)

    /// Reference to the evaluation value containing the time usage to show in this cell.
    #[graphql(name = "ref")]
    pub r#ref: Key,
}


/// Cell containing an amount of memory used for computation.
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct MemoryUsageCellContent {
    /// Maximum memory usage expected to be represented faithfully.
    /// Determines the scale of the representation (e.g., the units).
    pub max_relevant: MemoryUsage,

    /// Memory usage that should be presented as the main limit.
    pub primary_watermark: Option<MemoryUsage>,

    // TODO: add secondary watermarks (each with a title)

    /// Reference to the evaluation value containing the memory usage to show in this cell.
    #[graphql(name = "ref")]
    pub r#ref: Key,
}

#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct MessageCellContent {
    /// Reference to the evaluation value containing the message to show in this cell.
    #[graphql(name = "ref")]
    pub r#ref: Key,
}
