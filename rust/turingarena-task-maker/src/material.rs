extern crate mime_guess;

use std::convert::TryInto;
use task_maker_format::ioi;
use turingarena::content::*;
use turingarena::evaluation::record::*;
use turingarena::feedback::{table::*, *};
use turingarena::problem::material::*;
use turingarena::award::*;
use turingarena::submission::form::*;

fn subtasks_of(task: &ioi::Task) -> Vec<&ioi::SubtaskInfo> {
    let mut subtasks: Vec<_> = task.subtasks.values().collect();
    subtasks.sort_by(|a, b| a.id.cmp(&b.id));
    subtasks
}

fn testcases_of(subtask: &ioi::SubtaskInfo) -> Vec<&ioi::TestcaseInfo> {
    let mut testcases: Vec<_> = subtask.testcases.values().collect();
    testcases.sort_by(|a, b| a.id.cmp(&b.id));
    testcases
}

fn submission_form() -> Form {
    Form {
        fields: vec![Field {
            id: FieldId("solution".into()),
            title: vec![TextVariant {
                attributes: vec![],
                value: "Solution".into(),
            }],
            types: vec![FileType {
                id: FileTypeId("cpp".into()),
                title: vec![TextVariant {
                    attributes: vec![],
                    value: "C++".into(),
                }],
                extensions: vec![
                    FileTypeExtension(".cpp".into()),
                    FileTypeExtension(".cc".into()),
                ],
                primary_extension: FileTypeExtension(".cpp".into()),
            }],
        }],
    }
}

fn award_of(subtask: &ioi::SubtaskInfo) -> Award {
    Award {
        name: AwardName(format!("subtask.{}", subtask.id)),
        title: vec![TextVariant {
            attributes: vec![],
            value: format!("Subtask {}", subtask.id),
        }],
        content: if subtask.max_score > 0.0 {
            AwardContent::Score(ScoreAwardContent {
                range: ScoreRange {
                    // TODO: assuming IOI-like tasks have integer scores
                    precision: 0,
                    max: Score(subtask.max_score),
                },
            })
        } else {
            AwardContent::Badge(BadgeAwardContent)
        }

    }
}

fn cols() -> Vec<Col> {
    vec![
        Col {
            title: vec![TextVariant {
                attributes: vec![],
                value: format!("Case"),
            }],
            content: ColContent::RowNumber(RowNumberColContent {}),
        },
        Col {
            title: vec![TextVariant {
                attributes: vec![],
                value: format!("Score"),
            }],
            content: ColContent::Score(ScoreColContent {
                range: ScoreRange {
                    // FIXME: assuming per-test-case score has fixed precision
                    precision: 2,
                    max: Score(1.),
                },
            }),
        },
    ]
}

fn caption() -> Text {
    vec![TextVariant {
        attributes: vec![],
        value: format!("Test case results"),
    }]
}

fn row_group_of(subtask: &ioi::SubtaskInfo) -> RowGroup {
    RowGroup {
        title: vec![TextVariant {
            attributes: vec![],
            value: format!("Subtask {}", subtask.id),
        }],
        rows: testcases_of(subtask).into_iter().map(row_of).collect(),
    }
}

fn row_of(testcase: &ioi::TestcaseInfo) -> Row {
    Row {
        content: RowContent::Data,
        cells: vec![
            Cell {
                content: CellContent::RowNumber(RowNumberCellContent {
                    number: testcase.id.try_into().expect("Testcase ID too large"),
                }),
            },
            Cell {
                content: CellContent::Score(ScoreCellContent {
                    range: ScoreRange {
                        precision: 2,
                        max: Score(1.),
                    },
                    r#ref: Key(format!("testcase.{}.score", testcase.id)),
                }),
            },
        ],
    }
}

fn files_in_dir(dir_path: &std::path::PathBuf) -> impl Iterator<Item = std::path::PathBuf> {
    std::fs::read_dir(dir_path)
        .expect("unable to read_dir")
        .map(|entry| entry.expect("unable to read_dir").path())
}

fn attachment_at_path(file_path: std::path::PathBuf) -> Attachment {
    Attachment {
        title: vec![TextVariant {
            attributes: vec![],
            value: file_path
                .file_name()
                .unwrap()
                .to_string_lossy()
                .into_owned(),
        }],
        file: vec![FileVariant {
            attributes: vec![],
            name: Some(FileName(
                file_path
                    .file_name()
                    .unwrap()
                    .to_string_lossy()
                    .into_owned(),
            )),
            r#type: mime_guess::from_path(&file_path)
                .first_raw()
                .map(|t| MediaType(t.to_owned())),
            content: FileContent(std::fs::read(&file_path.to_string_lossy().as_ref()).unwrap()),
        }],
    }
}

fn statement_of(booklet: &ioi::Booklet) -> FileVariant {
    FileVariant {
        attributes: vec![VariantAttribute {
            key: "language".to_owned(),
            value: booklet.config().language.to_owned(),
        }],
        name: Some(FileName(
            booklet
                .dest()
                .file_name()
                .unwrap()
                .to_string_lossy()
                .into_owned(),
        )),
        r#type: Some(MediaType("application/pdf".to_owned())),
        content: FileContent(std::fs::read(booklet.dest()).expect("Unable to read statement file")),
    }
}

pub fn gen_material(task: &ioi::Task) -> Material {
    Material {
        title: vec![TextVariant {
            attributes: vec![],
            value: task.title.clone().into(),
        }],
        statement: task.booklets.iter().map(statement_of).collect(),
        attachments: files_in_dir(&task.path.join("att"))
            .map(attachment_at_path)
            .collect(),
        submission_form: submission_form(),
        awards: {
            subtasks_of(task)
                .into_iter()
                .filter(|s| s.max_score > 0.0)
                .map(award_of)
                .collect()
        },
        feedback: vec![Section::Table(TableSection {
            caption: caption(),
            cols: cols(),
            row_groups: subtasks_of(task).into_iter().map(row_group_of).collect(),
        })],
    }
}
