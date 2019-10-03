extern crate serde;

use super::content::*;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Clone)]
pub struct Attachment {
    pub title: Text,
    pub file: File,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct Problem {
    pub title: Text,
    pub statement: File,
    pub attachments: Vec<Attachment>,
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn it_works() {
        println!(
            "{}",
            serde_json::to_string_pretty(&Problem {
                title: vec![TextVariant {
                    attributes: vec!["language:en-US".to_owned()],
                    value: "Title".to_owned(),
                }],
                statement: vec![FileVariant {
                    attributes: vec!["language:en-US".to_owned()],
                    name: Some(FileName("english.pdf".to_owned())),
                    r#type: Some(MediaType("application/pdf".to_owned())),
                    content: vec![],
                }],
                attachments: vec![Attachment {
                    title: vec![TextVariant {
                        attributes: vec!["language:en-US".to_owned()],
                        value: "Skeleton".to_owned(),
                    }],
                    file: vec![FileVariant {
                        attributes: vec![],
                        name: Some(FileName("skeleton.cpp".to_owned())),
                        r#type: None,
                        content: vec![],
                    }],
                }],
            })
            .unwrap()
        );
    }
}
