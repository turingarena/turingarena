extern crate base64;
extern crate base64_serde;
extern crate serde;

use base64::STANDARD;
use base64_serde::base64_serde_type;
use serde::{Deserialize, Serialize};

base64_serde_type!(Base64Standard, STANDARD);

/// https://tools.ietf.org/html/bcp47
#[derive(Serialize, Deserialize, Clone)]
pub struct LanguageTag(pub String);

/// https://tools.ietf.org/html/rfc7231#section-3.1.1.1
#[derive(Serialize, Deserialize, Clone)]
pub struct MediaType(pub String);

#[derive(Serialize, Deserialize, Clone)]
pub struct FileName(pub String);

#[derive(Serialize, Deserialize, Clone)]
pub struct TextVariant {
    #[serde(default)]
    pub attributes: VariantAttributes,

    pub value: String,
}

pub type VariantAttributes = Vec<String>;
pub type Text = Vec<TextVariant>;

#[derive(Serialize, Deserialize, Clone)]
pub struct FileVariant {
    #[serde(default)]
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
