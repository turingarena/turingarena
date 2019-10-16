#![doc(include = "README.md")]

extern crate serde;

use serde::{Deserialize, Serialize};

/// Wraps a language tag string, as defined in
/// https://tools.ietf.org/html/bcp47
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLScalarValue)]
pub struct LanguageTag(pub String);

/// Wraps a media type string, as defined in
/// https://tools.ietf.org/html/rfc7231#section-3.1.1.1
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLScalarValue)]
pub struct MediaType(pub String);

/// Wraps a sanitized file name.
/// Allows extensions, but no path components.
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLScalarValue)]
pub struct FileName(pub String);

mod file;
pub use file::FileContent;

/// A variant of a text (say, for a given locale).
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct TextVariant {
    /// Attributes of this variant, used for content negotiation
    #[serde(default)]
    pub attributes: Vec<VariantAttribute>,

    /// Actual text of this variant
    pub value: String,
}

/// An attribute of a variant, used for content negotiation
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct VariantAttribute {
    pub key: String,
    pub value: String,
}

/// A text to show to users, expressed as a collection of variants (for content negotiation).
pub type Text = Vec<TextVariant>;

/// A variant of a file (say, for a given locale).
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct FileVariant {
    /// Attributes of this variant, used for content negotiation
    #[serde(default)]
    pub attributes: Vec<VariantAttribute>,

    /// Name of this file, if relevant
    pub name: Option<FileName>,
    /// Media type of this file, if relevant
    pub r#type: Option<MediaType>,

    /// Byte content of this file
    pub content: FileContent,
}

/// A file, expressed as a collection of variants (for content negotiation).
pub type File = Vec<FileVariant>;

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
