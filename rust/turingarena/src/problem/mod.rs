#![doc(include = "README.md")]

extern crate serde;

use crate::{content::*, feedback, score, submission};
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
    /// File rendered to users, containing the description of this problem
    pub statement: File,
    /// A collection of zero or more attachments for this problem
    pub attachments: Vec<Attachment>,
    pub submission_form: submission::form::Form,
    pub scored_items: Vec<score::ScoredItem>,
    pub feedback: feedback::Template,
}

#[cfg(test)]
mod tests {
    use super::{feedback::table::*, submission::form::*, *};
    use crate::evaluation::record::Key;
    use score::*;
    #[test]
    fn it_works() {
        let language_attr = VariantAttribute {
            key: "language".to_owned(),
            value: "en-US".to_owned(),
        };
        println!(
            "{}",
            serde_json::to_string_pretty(&Problem {
                title: vec![TextVariant {
                    attributes: vec![language_attr.clone()],
                    value: "Title".to_owned(),
                }],
                statement: vec![FileVariant {
                    attributes: vec![language_attr.clone()],
                    name: Some(FileName("english.pdf".to_owned())),
                    r#type: Some(MediaType("application/pdf".to_owned())),
                    content: vec![],
                }],
                attachments: vec![Attachment {
                    title: vec![TextVariant {
                        attributes: vec![language_attr.clone()],
                        value: "Skeleton".to_owned(),
                    }],
                    file: vec![FileVariant {
                        attributes: vec![],
                        name: Some(FileName("skeleton.cpp".to_owned())),
                        r#type: None,
                        content: vec![],
                    }],
                }],
                submission_form: Form {
                    fields: vec![Field {
                        id: FieldId("solution".to_owned()),
                        title: vec![TextVariant {
                            attributes: vec![language_attr.clone()],
                            value: "Solution".to_owned(),
                        }],
                        types: vec![FileType {
                            id: FileTypeId("cpp".to_owned()),
                            title: vec![TextVariant {
                                attributes: vec![language_attr.clone()],
                                value: "C/C++".to_owned(),
                            }],
                            extensions: vec![FileTypeExtension(".cpp".to_owned())],
                            primary_extension: FileTypeExtension(".cpp".to_owned()),
                        }],
                    }]
                },
                scored_items: vec![
                    ScoredItem {
                        title: vec![TextVariant {
                            attributes: vec![language_attr.clone()],
                            value: "Sub-task 1".to_owned(),
                        }],
                        range: score::Range {
                            precision: 2,
                            max: Score(40.),
                        },
                    },
                    ScoredItem {
                        title: vec![TextVariant {
                            attributes: vec![language_attr.clone()],
                            value: "Sub-task 2".to_owned(),
                        }],
                        range: score::Range {
                            precision: 2,
                            max: Score(60.),
                        },
                    }
                ],
                feedback: vec![feedback::Section::Table(Table {
                    cols: vec![
                        Col {
                            title: vec![TextVariant {
                                attributes: vec![language_attr.clone()],
                                value: "Test Case".to_owned(),
                            }],
                            content: ColContent::Index,
                        },
                        Col {
                            title: vec![TextVariant {
                                attributes: vec![language_attr.clone()],
                                value: "Score".to_owned(),
                            }],
                            content: ColContent::Score {
                                range: score::Range {
                                    precision: 2,
                                    max: Score(100.),
                                }
                            },
                        }
                    ],
                    row_groups: vec![
                        RowGroup {
                            title: vec![TextVariant {
                                attributes: vec![language_attr.clone()],
                                value: "Subtask 1".to_owned(),
                            }],
                            rows: vec![Row {
                                content: RowContent::Data,
                                cells: vec![
                                    Cell {
                                        content: CellContent::Index(1),
                                    },
                                    Cell {
                                        content: CellContent::Score {
                                            range: score::Range {
                                                precision: 2,
                                                max: Score(50.),
                                            },
                                            r#ref: Key("subtask.1.testcase.1.score".into()),
                                        },
                                    },
                                ]
                            },],
                        },
                        RowGroup {
                            title: vec![TextVariant {
                                attributes: vec![language_attr.clone()],
                                value: "Subtask 1".to_owned(),
                            }],
                            rows: vec![Row {
                                content: RowContent::Data,
                                cells: vec![
                                    Cell {
                                        content: CellContent::Index(2),
                                    },
                                    Cell {
                                        content: CellContent::Score {
                                            range: score::Range {
                                                precision: 2,
                                                max: Score(50.),
                                            },
                                            r#ref: Key("subtask.2.testcase.2.score".into()),
                                        },
                                    },
                                ]
                            },],
                        },
                    ],
                })],
            })
            .unwrap()
        );
    }
}
