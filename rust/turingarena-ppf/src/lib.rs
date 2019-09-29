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

/// https://tools.ietf.org/html/rfc7231#section-3.1.1.1
#[derive(Serialize, Deserialize, Clone)]
pub struct MediaType(String);

#[derive(Serialize, Deserialize, Clone)]
pub struct VariantAttributes {
    language: Option<LanguageTag>,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct FileName(String);

#[derive(Serialize, Deserialize, Clone)]
pub struct TextVariant {
    attributes: VariantAttributes,
    value: String,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct FileVariant {
    attributes: VariantAttributes,
    name: Option<FileName>,
    r#type: Option<MediaType>,
    #[serde(with = "Base64Standard")]
    content: Vec<u8>,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct Problem {
    title: Vec<TextVariant>,
    statement: Vec<FileVariant>,
    attachments: HashMap<String, FileVariant>,
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn it_works() {
        println!(
            "{}",
            serde_json::to_string(&Problem {
                title: vec![TextVariant {
                    attributes: VariantAttributes {
                        language: Some(LanguageTag("en-US".into())),
                    },
                    value: "Title".into(),
                }],
                statement: vec![FileVariant {
                    attributes: VariantAttributes {
                        language: Some(LanguageTag("en-US".into())),
                    },
                    name: Some(FileName("english.pdf".into())),
                    r#type: Some(MediaType("application/pdf".into())),
                    content: vec![],
                }],
                attachments: {
                    let mut map = HashMap::new();
                    map.insert(
                        "skeleton".into(),
                        FileVariant {
                            attributes: VariantAttributes { language: None },
                            name: Some(FileName("skeleton.cpp".into())),
                            r#type: None,
                            content: vec![0],
                        },
                    );
                    map
                },
            })
            .unwrap()
        );
    }
}
