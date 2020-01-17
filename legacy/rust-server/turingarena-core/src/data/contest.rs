//! Data types to represent general information about a contest

use crate::data::content::{File, Text};

/// A file that users can download.
#[derive(Serialize, Deserialize, Clone, Debug, juniper::GraphQLObject)]
pub struct ContestResource {
    /// Name of this resource, as shown to users.
    pub title: Text,
    /// Displayable file for this attachment.
    pub file: File,
}

/// A file that users can download.
#[derive(Serialize, Deserialize, Clone, Debug, juniper::GraphQLObject)]
pub struct ContestAttachment {
    /// Name of this attachment, as shown to users.
    pub title: Text,
    /// Downloadable file for this attachment.
    pub file: File,
}

/// General information about a contest.
#[derive(Serialize, Deserialize, Clone, Debug, juniper::GraphQLObject)]
pub struct ContestMaterial {
    /// Title of the contest, as shown to the user
    pub title: Text,

    /// Main document shown to the user for this contest
    pub description: File,

    /// Extra documents accessible to the user
    pub resources: Vec<ContestResource>,

    /// A collection of zero or more attachments for this contest.
    pub attachments: Vec<ContestAttachment>,
}
