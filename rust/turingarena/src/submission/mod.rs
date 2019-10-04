#![doc(include = "README.md")]

extern crate serde;

use super::content::*;
use serde::{Deserialize, Serialize};

/// Contains types to define a submission form
pub mod form {
    use super::*;

    /// Wraps a string identifying a field in a submission
    #[derive(Serialize, Deserialize, Clone)]
    pub struct FieldId(pub String);

    /// Wraps a string identifying a file type for a field in a submission
    #[derive(Serialize, Deserialize, Clone)]
    pub struct FileTypeId(pub String);

    /// Describes a field of a submission form
    #[derive(Serialize, Deserialize, Clone)]
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
    #[derive(Serialize, Deserialize, Clone)]
    pub struct FileTypeExtension(pub String);

    #[derive(Serialize, Deserialize, Clone)]
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
    #[derive(Serialize, Deserialize, Clone)]
    pub struct Form {
        /// List of fields of this form
        pub fields: Vec<Field>,
    }
}

/// Contains types to represent a submission available on the local machine
mod local {
    use super::*;
    use std::path;

    /// Value of a submission field
    #[derive(Clone)]
    pub struct FieldValue {
        /// Local path of a submission file.
        /// File name must follow the format `<field_id>.<file_type_id>.<ext>`.
        pub path: Option<path::PathBuf>,
    }

    /// Content of a submission stored on the local filesystem.
    #[derive(Clone)]
    pub struct Local {
        /// Submission form associated with this submission
        pub form: form::Form,

        /// A value for each field of the associated form.
        /// Values are given in
        pub field_values: Vec<FieldValue>,
    }
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
