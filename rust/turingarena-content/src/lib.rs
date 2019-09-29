extern crate base64;
extern crate serde;

extern crate base64_serde;

use base64::STANDARD;
use base64_serde::base64_serde_type;
use serde::{Deserialize, Serialize};

use std::collections::HashMap;

base64_serde_type!(Base64Standard, STANDARD);

/// https://tools.ietf.org/html/bcp47
#[derive(Serialize, Deserialize, Clone)]
pub struct LanguageTag(String);

impl From<&str> for LanguageTag {
    fn from(s: &str) -> LanguageTag {
        // TODO: validation
        LanguageTag(s.to_owned())
    }
}

/// https://tools.ietf.org/html/rfc7231#section-3.1.1.1
#[derive(Serialize, Deserialize, Clone)]
pub struct MediaType(String);

impl From<&str> for MediaType {
    fn from(s: &str) -> MediaType {
        // TODO: validation
        MediaType(s.to_owned())
    }
}

#[derive(Serialize, Deserialize, Clone, Default)]
pub struct VariantAttributes(HashMap<String, String>);

pub struct VariantAttributesBuilder(HashMap<String, String>);

impl VariantAttributes {
    pub fn builder() -> VariantAttributesBuilder {
        VariantAttributesBuilder(HashMap::new())
    }
}

impl VariantAttributesBuilder {
    pub fn language(mut self, tag: LanguageTag) -> VariantAttributesBuilder {
        self.0.insert("language".into(), tag.0);
        self
    }

    pub fn build(self) -> VariantAttributes {
        VariantAttributes(self.0)
    }
}

#[derive(Serialize, Deserialize, Clone)]
pub struct FileName(String);

impl From<&str> for FileName {
    fn from(s: &str) -> FileName {
        // TODO: validation
        FileName(s.into())
    }
}

#[derive(Serialize, Deserialize, Clone)]
pub struct TextVariant {
    pub attributes: VariantAttributes,
    pub value: String,
}

pub type Text = Vec<TextVariant>;

#[derive(Serialize, Deserialize, Clone)]
pub struct FileVariant {
    pub attributes: VariantAttributes,
    pub name: Option<FileName>,
    pub r#type: Option<MediaType>,
    #[serde(with = "Base64Standard")]
    pub content: Vec<u8>,
}

pub type File = Vec<FileVariant>;

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
