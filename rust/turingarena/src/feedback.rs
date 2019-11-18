//! Data-types for feedback templates.

extern crate juniper;

use crate::juniper_ext::*;
use serde::{Deserialize, Serialize};
use table::TableSection;

/// A feedback template, consisting of a list of sections.
/// The template can be rendered to users before evaluation,
/// and gradually filled with data coming from the evaluation.
pub type Template = Vec<Section>;

/// A section in the feedback template.
#[derive(Serialize, Deserialize, Clone, GraphQLUnionFromEnum)]
pub enum Section {
    /// A section containing tabular data.
    Table(TableSection),
}

pub mod valence {
    use serde::{Deserialize, Serialize};

    /// Qualitative feeling associated to a feedback item.
    ///
    /// These enum variants are meant to be used only to control the appearance of feedback items.
    /// They might not all be applicable in every context,
    /// and their precise interpretation may depend on the context.
    /// However, they are all intentionally gathered together for simplicity.
    #[derive(Debug, Copy, Clone, Serialize, Deserialize, juniper::GraphQLEnum)]
    pub enum Valence {
        /// A successful result.
        /// E.g., a award is given full score.
        Success,
        /// A partial success.
        /// E.g., a award is given partial score.
        Partial,
        /// A failed result.
        /// E.g., time limit exceeded causes the loss of an award.
        Failure,
        /// The user should pay attention to something because it could result in a future failure.
        /// E.g., memory usage approaches the limit.
        Warning,
        /// An operation is completed successfully, as usually expected.
        /// E.g., a submitted source compiles correctly.
        Nominal,
        /// An operation is not performed, because a previous _success_ makes it unnecessary.
        /// E.g., an award is not evaluated because already achieved.
        Skipped,
        /// An operation is not performed, because irrelevant in the context.
        /// E.g., the compilation of a source program written in Python is note performed.
        Ignored,
        /// An operation is not performed, because a previous _failure_ makes it unnecessary.
        /// E.g., a large test case is not evaluated because a solution fails in a smaller one.
        Blocked,
    }
}

/// Tabular feedback.
pub mod table {
    use serde::{Deserialize, Serialize};

    use crate::juniper_ext::*;
    use crate::rusage::{MemoryUsage, TimeUsage};
    use crate::{award, content::Text, evaluation::record::Key};

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

    /// Describes the kind of data shown in a column.
    #[derive(Serialize, Deserialize, Clone, GraphQLUnionFromEnum)]
    #[serde(rename_all = "snake_case")]
    pub enum ColContent {
        RowTitle(RowTitleColContent),
        RowNumber(RowNumberColContent),
        Score(ScoreColContent),
        Message(MessageColContent),
        TimeUsage(TimeUsageColContent),
        MemoryUsage(MemoryUsageColContent),
    }

    /// Column of row titles.
    /// Cells must contain `CellContent::RowTitle`.
    #[derive(Serialize, Deserialize, Clone, GraphQLObjectFromUnit)]
    pub struct RowTitleColContent;

    /// Column of row numbers.
    /// Cells must contain `CellContent::RowNumber`.
    #[derive(Serialize, Deserialize, Clone, GraphQLObjectFromUnit)]
    pub struct RowNumberColContent;

    /// Column of scores.
    /// Cells must contain `CellContent::Score` or `CellContent::Missing`.
    #[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
    pub struct ScoreColContent {
        /// Score range that applies to all column cells.
        pub range: award::ScoreRange,
    }

    /// Column of text messages.
    /// Cells must contain `CellContent::Message` or `CellContent::Missing`.
    #[derive(Serialize, Deserialize, Clone, GraphQLObjectFromUnit)]
    pub struct MessageColContent;

    /// Column containing amounts of time used for computation.
    /// Cells must contain `CellContent::TimeUsage`.
    #[derive(Serialize, Deserialize, Clone, GraphQLObjectFromUnit)]
    pub struct TimeUsageColContent;

    /// Column containing amounts of memory used for computation.
    /// Cells must contain `CellContent::MemoryUsage`.
    #[derive(Serialize, Deserialize, Clone, GraphQLObjectFromUnit)]
    pub struct MemoryUsageColContent;

    /// Describes the kind of data shown in a cell.
    #[derive(Serialize, Deserialize, Clone, GraphQLUnionFromEnum)]
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

    /// Cell containing no value.
    #[derive(Serialize, Deserialize, Clone, GraphQLObjectFromUnit)]
    pub struct MissingCellContent;

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
        pub key: Key,
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
        /// Time usage to show in this cell (reference).
        pub key: Key,
        /// Valence associated with this cell, if any (reference).
        pub valence_key: Option<Key>,
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
        /// Memory usage to show in this cell (reference).
        pub key: Key,
        /// Valence associated with this cell, if any (reference).
        pub valence_key: Option<Key>,
    }

    #[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
    pub struct MessageCellContent {
        /// Message to show in this cell (reference).
        pub key: Key,
        /// Valence associated with this cell, if any (reference).
        pub valence_key: Option<Key>,
    }
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
