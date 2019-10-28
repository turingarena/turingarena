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
