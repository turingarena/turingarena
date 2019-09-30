extern crate serde;
extern crate turingarena_content;
#[macro_use]
extern crate derive_builder;

use serde::{Deserialize, Serialize};
use turingarena_content::*;

#[derive(Serialize, Deserialize, Clone, Builder)]
pub struct Attachment {
    title: Text,
    file: File,
}

#[derive(Serialize, Deserialize, Clone, Builder)]
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
                title: vec![TextVariantBuilder::default()
                    .attributes(
                        VariantAttributesBuilder::default()
                            .language("en-US".parse().unwrap())
                            .build()
                    )
                    .value("Title")
                    .build()
                    .unwrap()],
                statement: vec![FileVariantBuilder::default()
                    .attributes(
                        VariantAttributesBuilder::default()
                            .language("en-US".parse().unwrap())
                            .build()
                    )
                    .name("english.pdf".parse().unwrap())
                    .r#type("application/pdf".parse().unwrap())
                    .content(vec![])
                    .build()
                    .unwrap()],
                attachments: vec![AttachmentBuilder::default()
                    .title(vec![TextVariantBuilder::default()
                        .attributes(
                            VariantAttributesBuilder::default()
                                .language("en-US".parse().unwrap())
                                .build()
                        )
                        .value("Title")
                        .build()
                        .unwrap()])
                    .file(vec![FileVariantBuilder::default()
                        .name("skeleton.cpp".parse().unwrap())
                        .content(vec![])
                        .build()
                        .unwrap()])
                    .build()
                    .unwrap()],
            })
            .unwrap()
        );
    }
}
