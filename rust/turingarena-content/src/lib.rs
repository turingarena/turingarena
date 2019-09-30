extern crate base64;
extern crate serde;

extern crate base64_serde;

use base64::STANDARD;
use base64_serde::base64_serde_type;
use serde::{Deserialize, Serialize};

use std::collections::HashMap;
use std::str::FromStr;

base64_serde_type!(Base64Standard, STANDARD);

/// https://tools.ietf.org/html/bcp47
#[derive(Serialize, Deserialize, Clone)]
pub struct LanguageTag(String);

impl FromStr for LanguageTag {
    type Err = ();
    fn from_str(s: &str) -> Result<LanguageTag, Self::Err> {
        // TODO: validation
        Ok(LanguageTag(s.to_owned()))
    }
}

/// https://tools.ietf.org/html/rfc7231#section-3.1.1.1
#[derive(Serialize, Deserialize, Clone)]
pub struct MediaType(String);

impl FromStr for MediaType {
    type Err = ();
    fn from_str(s: &str) -> Result<MediaType, Self::Err> {
        // TODO: validation
        Ok(MediaType(s.to_owned()))
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

impl FromStr for FileName {
    type Err = ();
    fn from_str(s: &str) -> Result<FileName, Self::Err> {
        // TODO: validation
        Ok(FileName(s.into()))
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
