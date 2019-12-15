use serde::{Deserialize, Serialize};

use crate::content::*;
use crate::juniper_ext::*;

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

/// A submission
#[derive(Clone)]
pub struct Submission {
    /// Submission form associated with this submission
    /// pub form: Form,

    /// A value for each field of the associated form.
    pub field_values: Vec<FieldValue>,
}

/// Value of a submission field
#[derive(Clone)]
pub struct FieldValue {
    pub field: FieldId,
    pub file: File,
}

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
