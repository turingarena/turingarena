extern crate base64;
extern crate base64_serde;
extern crate serde;

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

#[derive(Default)]
pub struct VariantAttributesBuilder(HashMap<String, String>);

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

#[derive(Serialize, Deserialize, Clone, Builder)]
pub struct TextVariant {
    #[builder(default)]
    attributes: VariantAttributes,
    #[builder(setter(into))]
    value: String,
}

pub type Text = Vec<TextVariant>;

#[derive(Serialize, Deserialize, Clone, Builder)]
pub struct FileVariant {
    #[builder(default)]
    attributes: VariantAttributes,
    #[builder(setter(strip_option), default)]
    name: Option<FileName>,
    #[builder(setter(strip_option), default)]
    r#type: Option<MediaType>,
    #[serde(with = "Base64Standard")]
    #[builder(setter(into))]
    content: Vec<u8>,
}

pub type File = Vec<FileVariant>;

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
