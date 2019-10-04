#![doc(include = "README.md")]

extern crate serde;

use super::content::*;
use serde::{Deserialize, Serialize};

/// A file that users can download
#[derive(Serialize, Deserialize, Clone)]
pub struct Attachment {
    /// Name of this attachment, as shown to users
    pub title: Text,
    /// Downloadable file for this attachment
    pub file: File,
}

/// Meta-data of a problem
#[derive(Serialize, Deserialize, Clone)]
pub struct Problem {
    /// Name of this problem, as shown to users
    pub title: Text,
    /// File rendered to users, containing the description of the problem
    pub statement: File,
    /// A collection of zero or more attachments
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
