#![doc(include = "README.md")]

extern crate juniper;
extern crate serde;

use serde::{Deserialize, Serialize};

use crate::content::*;
use crate::juniper_ext::*;

/// Contains types to define a submission form
pub mod form {
    use super::*;

    /// Wraps a string identifying a field in a submission
    #[derive(Serialize, Deserialize, Clone, GraphQLNewtype)]
    pub struct FieldId(pub String);

    /// Wraps a string identifying a file type for a field in a submission
    #[derive(Serialize, Deserialize, Clone, GraphQLNewtype)]
    pub struct FileTypeId(pub String);

    /// Describes a field of a submission form
    #[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
    pub struct Field {
        /// ID of this field
        pub id: FieldId,
        /// Name of this field, to be shown to users
        pub title: Text,
        /// List of possible file types accepted for this field.
        /// File type is selectable by user, but may be detected automatically from the file extension.
        pub types: Vec<FileType>,
    }

    /// Wraps a file extension.
    /// Should start with a dot, followed by a non-empty ASCII alphanumeric string.
    #[derive(Serialize, Deserialize, Clone, GraphQLNewtype)]
    pub struct FileTypeExtension(pub String);

    #[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
    pub struct FileType {
        /// ID of this file type
        pub id: FileTypeId,
        /// Name of this file type, to be shown to users
        pub title: Text,
        /// File name extensions associated with this type.
        /// Used to identify the type automatically from the extension of a submitted file.
        pub extensions: Vec<FileTypeExtension>,
        /// File name extension used when storing files of this type
        pub primary_extension: FileTypeExtension,
    }

    /// Describes the schema of a submission
    #[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
    pub struct Form {
        /// List of fields of this form
        pub fields: Vec<Field>,
    }
}

#[derive(Clone)]
pub struct Submission<T: Clone> {
    /// Submission form associated with this submission
    /// pub form: form::Form,

    /// A value for each field of the associated form.
    pub field_values: Vec<FieldValue<T>>,
}

/// Value of a submission field
#[derive(Clone)]
pub struct FieldValue<T: Clone> {
    pub field: form::FieldId,
    pub file: T,
}

/// Contains types to represent a submission stored on the local machine
pub mod local {
    use std::path;

    /// A submission file stored on the local filesystem.
    #[derive(Clone)]
    pub struct File {
        /// Local path of a submission file.
        /// File name should follow the format `<field_id>.<file_type_id>.<ext>`.
        pub path: path::PathBuf,
    }

    /// A submission stored on the local filesystem.
    pub type Submission = super::Submission<File>;
}

/// Contains types to represent a submission in memory
pub mod mem {
    /// Wraps a sanitized file name.
    #[derive(Clone)]
    pub struct FileName(pub String);

    /// A submission file stored on the local filesystem.
    #[derive(Clone)]
    pub struct File {
        /// Name of the submitted file.
        pub name: FileName,
        /// Byte content of the submitted file.
        pub content: Vec<u8>,
    }

    /// A field of a submission stored in memory.
    pub type FieldValue = super::FieldValue<File>;
    /// A submission stored in memory.
    pub type Submission = super::Submission<File>;
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
