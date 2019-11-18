//! Problem definitions and runners.
//!
//! In our case, a "problem" has the following characteristics:
//!
//! * describes a challenge, which requires the submission of a "solution",
//! * each solution, submitted by a single user or team, is evaluated independently from other submission,
//! * optionally, the evaluation assigns a numerical score to a solution,
//!   possibly separated into different "scored items",
//! * optionally, the evaluation generates a detailed feedback for the submission
//!  (e.g., explaining the assigned score).
//!
//! Problems are meant to be used in contests, as well as in other context (e.g., a training website).

use super::juniper_ext::*;
use serde::{Deserialize, Serialize};

/// Wraps a string representing the name of a problem.
/// Used only to identify a problem. Should never be shown to (non-admin) users.
///
/// Represents the default name used to identify a problem within a contest,
/// in a way similar to names of Cargo dependencies.
/// It could be overridden (as with the `package` option in `Cargo.toml`),
/// in the rare case two problems with the same name are desired in the same contest
/// (or two versions of the same problem).
#[derive(Debug, Serialize, Deserialize, Clone, GraphQLNewtype)]
pub struct ProblemName(pub String);

/// Generated material for problems.
///
/// Includes problem statement, attchments, submission form fields, scorables, and feedback format.
pub mod material {
    extern crate juniper;
    extern crate serde;

    use crate::{award, content::*, feedback, submission};
    use serde::{Deserialize, Serialize};

    /// A file that users can download.
    #[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
    pub struct Attachment {
        /// Name of this attachment, as shown to users.
        pub title: Text,
        /// Downloadable file for this attachment.
        pub file: File,
    }

    /// Meta-data of a problem
    #[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
    pub struct Material {
        /// Title of this problem, as shown to users.
        pub title: Text,
        /// File rendered to users, containing the description of this problem.
        pub statement: File,
        /// A collection of zero or more attachments for this problem.
        pub attachments: Vec<Attachment>,
        /// Form to show to users, for submitting solutions.
        pub submission_form: submission::form::Form,
        /// Awards that this problem can assign to submissions.
        pub awards: Vec<award::Award>,
        /// Template of the feedback to show to users, for a submitted solution.
        pub feedback: feedback::Template,
    }
}

/// Contains a trait to implement to support a problem format.
pub mod driver {
    use std::path;

    use super::*;
    use crate::*;

    pub struct ProblemStat {
        pub name: ProblemName,
    }

    pub struct ProblemPack(pub path::PathBuf);

    pub trait ProblemDriver {
        type StatError;
        type Error;

        fn stat(pack: ProblemPack) -> Result<ProblemStat, Self::StatError>;
        fn gen_material(pack: ProblemPack) -> Result<material::Material, Self::Error>;
        fn evaluate(
            pack: ProblemPack,
            submission: submission::mem::Submission,
        ) -> evaluation::mem::Evaluation;
    }
}
