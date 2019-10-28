#![doc(include = "README.md")]

extern crate juniper;
extern crate serde;

use crate::{award, content::*, feedback, submission};
use serde::{Deserialize, Serialize};

/// A file that users can download.
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct Attachment {
    /// Name of this attachment, as shown to users.
    pub title: Text,
    /// Downloadable file for this attachment.
    pub file: File,
}

/// Meta-data of a problem
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLObject)]
pub struct Material {
    /// Title of this problem, as shown to users.
    pub title: Text,
    /// File rendered to users, containing the description of this problem.
    pub statement: File,
    /// A collection of zero or more attachments for this problem.
    pub attachments: Vec<Attachment>,
    /// Form to show to users, for submitting solutions.
    pub submission_form: submission::form::Form,
    /// Awards that this problem can assign to submissions.
    pub awards: Vec<award::Award>,
    /// Template of the feedback to show to users, for a submitted solution.
    pub feedback: feedback::Template,
}

#[cfg(test)]
mod tests {
    use super::{feedback::table::*, submission::form::*, *};
    use crate::evaluation::record::Key;
    use award::*;
    #[test]
    fn it_works() {
        let language_attr = VariantAttribute {
            key: "language".to_owned(),
            value: "en-US".to_owned(),
        };
        println!(
            "{}",
            serde_json::to_string_pretty(&Material {
                title: vec![TextVariant {
                    attributes: vec![language_attr.clone()],
                    value: "Title".to_owned(),
                }],
                statement: vec![FileVariant {
                    attributes: vec![language_attr.clone()],
                    name: Some(FileName("english.pdf".to_owned())),
                    r#type: Some(MediaType("application/pdf".to_owned())),
                    content: FileContent(vec![]),
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
                        content: FileContent(vec![]),
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
                    }],
                },
                scored_items: vec![
                    ScoredItem {
                        title: vec![TextVariant {
                            attributes: vec![language_attr.clone()],
                            value: "Sub-task 1".to_owned(),
                        }],
                        range: award::ScoreRange {
                            precision: 2,
                            max: Score(40.),
                        },
                    },
                    ScoredItem {
                        title: vec![TextVariant {
                            attributes: vec![language_attr.clone()],
                            value: "Sub-task 2".to_owned(),
                        }],
                        range: award::ScoreRange {
                            precision: 2,
                            max: Score(60.),
                        },
                    },
                ],
                feedback: vec![feedback::Section::Table(feedback::table::TableSection {
                    caption: vec![TextVariant {
                        attributes: vec![language_attr.clone()],
                        value: "Test cases".to_owned(),
                    }],
                    cols: vec![
                        Col {
                            title: vec![TextVariant {
                                attributes: vec![language_attr.clone()],
                                value: "Case".to_owned(),
                            }],
                            content: ColContent::RowNumber(RowNumberColContent {}),
                        },
                        Col {
                            title: vec![TextVariant {
                                attributes: vec![language_attr.clone()],
                                value: "Score".to_owned(),
                            }],
                            content: ColContent::Score(ScoreColContent {
                                range: award::ScoreRange {
                                    precision: 2,
                                    max: Score(100.),
                                },
                            }),
                        },
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
                                        content: CellContent::RowNumber(RowNumberCellContent {
                                            number: 1,
                                        }),
                                    },
                                    Cell {
                                        content: CellContent::Score(ScoreCellContent {
                                            range: award::ScoreRange {
                                                precision: 2,
                                                max: Score(50.),
                                            },
                                            key: Key("subtask.1.testcase.1.score".to_owned()),
                                        }),
                                    },
                                ],
                            }],
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
                                        content: CellContent::RowNumber(RowNumberCellContent {
                                            number: 2,
                                        }),
                                    },
                                    Cell {
                                        content: CellContent::Score(ScoreCellContent {
                                            range: award::ScoreRange {
                                                precision: 2,
                                                max: Score(50.),
                                            },
                                            key: Key("subtask.2.testcase.2.score".to_owned()),
                                        }),
                                    },
                                ],
                            }],
                        },
                    ],
                })],
            })
            .unwrap()
        );
    }
}
