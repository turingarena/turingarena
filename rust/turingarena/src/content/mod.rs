#![doc(include = "README.md")]

extern crate base64;
extern crate base64_serde;
extern crate serde;

use base64::STANDARD;
use base64_serde::base64_serde_type;
use serde::{Deserialize, Serialize};

base64_serde_type!(Base64Standard, STANDARD);

/// Wraps a language tag string, as defined in
/// https://tools.ietf.org/html/bcp47
#[derive(Serialize, Deserialize, Clone)]
pub struct LanguageTag(pub String);

/// Wraps a media type string, as defined in
/// https://tools.ietf.org/html/rfc7231#section-3.1.1.1
#[derive(Serialize, Deserialize, Clone)]
pub struct MediaType(pub String);

/// Wraps a sanitized file name.
/// Allows extensions, but no path components.
#[derive(Serialize, Deserialize, Clone)]
pub struct FileName(pub String);

/// A variant of a text (say, for a given locale).
#[derive(Serialize, Deserialize, Clone)]
pub struct TextVariant {
    /// Attributes of this variant, used for content negotiation
    #[serde(default)]
    pub attributes: Vec<VariantAttribute>,

    /// Actual text of this variant
    pub value: String,
}

/// An attribute of a variant, used for content negotiation
#[derive(Serialize, Deserialize, Clone)]
pub struct VariantAttribute {
    pub key: String,
    pub value: String,
}

/// A text to show to users, expressed as a collection of variants (for content negotiation).
pub type Text = Vec<TextVariant>;

/// A variant of a file (say, for a given locale).
#[derive(Serialize, Deserialize, Clone)]
pub struct FileVariant {
    /// Attributes of this variant, used for content negotiation
    #[serde(default)]
    pub attributes: Vec<VariantAttribute>,

    /// Name of this file, if relevant
    pub name: Option<FileName>,
    /// Media type of this file, if relevant
    pub r#type: Option<MediaType>,

    /// Byte content of this file
    #[serde(with = "Base64Standard")]
    pub content: Vec<u8>,
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
