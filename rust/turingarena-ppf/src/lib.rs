extern crate serde;
extern crate turingarena_content;

use serde::{Deserialize, Serialize};
use turingarena_content::*;

#[derive(Serialize, Deserialize, Clone)]
pub struct Attachment {
    title: Text,
    file: File,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct Problem {
    title: Text,
    statement: File,
    attachments: Vec<Attachment>,
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
                    attributes: VariantAttributes::builder()
                        .language("en-US".parse().unwrap())
                        .build(),
                    value: "Title".parse().unwrap(),
                }],
                statement: vec![FileVariant {
                    attributes: VariantAttributes::builder()
                        .language("en-US".parse().unwrap())
                        .build(),
                    name: Some("english.pdf".parse().unwrap()),
                    r#type: Some("application/pdf".parse().unwrap()),
                    content: vec![],
                }],
                attachments: vec![Attachment {
                    title: vec![TextVariant {
                        attributes: VariantAttributes::builder()
                            .language("en-US".parse().unwrap())
                            .build(),
                        value: "Skeleton".parse().unwrap(),
                    }],
                    file: vec![FileVariant {
                        attributes: VariantAttributes::default(),
                        name: Some("skeleton.cpp".parse().unwrap()),
                        r#type: None,
                        content: vec![0],
                    },],
                }],
            })
            .unwrap()
        );
    }
}
