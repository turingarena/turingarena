extern crate mime_guess;

use std::convert::TryInto;
use std::path::{Path, PathBuf};

use task_maker_format::ioi;

use super::*;

use award::*;
use content::*;
use evaluation::record::*;
use feedback::{table::*, *};
use problem::material::*;
use rusage::{MemoryUsage, TimeUsage};
use submission::*;

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
        title: vec![
            TextVariant {
                attributes: vec![],
                value: format!("Subtask {}", subtask.id),
            },
            TextVariant {
                attributes: vec![VariantAttribute {
                    key: "style".to_owned(),
                    value: "short".to_owned(),
                }],
                value: format!("ST {}", subtask.id),
            },
        ],
        content: if subtask.max_score > 0.0 {
            AwardContent::Score(ScoreAwardContent {
                range: ScoreRange {
                    // TODO: determine actual precision (may depend on the task)
                    precision: 0,
                    max: Score(subtask.max_score),
                    // TODO: determine whether partial scores are allowed (may depend on the task)
                    allow_partial: true,
                },
            })
        } else {
            AwardContent::Badge(BadgeAwardContent)
        },
    }
}

fn cols() -> Vec<Col> {
    vec![
        Col {
            title: vec![TextVariant {
                attributes: vec![],
                value: "Case".to_owned(),
            }],
            content: ColContent::RowNumber(RowNumberColContent {}),
        },
        Col {
            title: vec![TextVariant {
                attributes: vec![],
                value: "Time usage".to_owned(),
            }],
            content: ColContent::TimeUsage(TimeUsageColContent),
        },
        Col {
            title: vec![TextVariant {
                attributes: vec![],
                value: "Memory usage".to_owned(),
            }],
            content: ColContent::MemoryUsage(MemoryUsageColContent),
        },
        Col {
            title: vec![TextVariant {
                attributes: vec![],
                value: "Message".to_owned(),
            }],
            content: ColContent::Message(MessageColContent),
        },
        Col {
            title: vec![TextVariant {
                attributes: vec![],
                value: "Score".to_owned(),
            }],
            content: ColContent::Score(ScoreColContent {
                range: ScoreRange {
                    // TODO: determine actual precision
                    precision: 2,
                    max: Score(1.),
                    // TODO: determine if partial scores are actually allowed
                    allow_partial: true,
                },
            }),
        },
    ]
}

fn caption() -> Text {
    vec![TextVariant {
        attributes: vec![],
        value: "Test case results".to_owned(),
    }]
}

fn row_group_of(task: &ioi::Task, subtask: &ioi::SubtaskInfo) -> RowGroup {
    RowGroup {
        title: vec![TextVariant {
            attributes: vec![],
            value: format!("Subtask {}", subtask.id),
        }],
        rows: testcases_of(subtask)
            .into_iter()
            .map(|testcase| row_of(task, subtask, testcase))
            .collect(),
    }
}

fn row_of(task: &ioi::Task, _subtask: &ioi::SubtaskInfo, testcase: &ioi::TestcaseInfo) -> Row {
    Row {
        content: RowContent::Data,
        cells: vec![
            Cell {
                content: CellContent::RowNumber(RowNumberCellContent {
                    number: testcase.id.try_into().expect("Testcase ID too large"),
                }),
            },
            Cell {
                content: CellContent::TimeUsage(TimeUsageCellContent {
                    max_relevant: TimeUsage(task.time_limit.unwrap_or(10.0)),
                    primary_watermark: task.time_limit.map(TimeUsage),
                    key: Key(format!("testcase.{}.time_usage", testcase.id)),
                    valence_key: Some(Key(format!("testcase.{}.time_usage_valence", testcase.id))),
                }),
            },
            Cell {
                content: CellContent::MemoryUsage(MemoryUsageCellContent {
                    max_relevant: MemoryUsage(
                        (task.memory_limit.unwrap_or(1024) * 1024 * 1024 * 2) as i32,
                    ),
                    primary_watermark: task
                        .memory_limit
                        .map(|l| MemoryUsage((l * 1024 * 1024) as i32)),
                    key: Key(format!("testcase.{}.memory_usage", testcase.id)),
                    valence_key: Some(Key(format!(
                        "testcase.{}.memory_usage_valence",
                        testcase.id
                    ))),
                }),
            },
            Cell {
                content: CellContent::Message(MessageCellContent {
                    key: Key(format!("testcase.{}.message", testcase.id)),
                    valence_key: Some(Key(format!("testcase.{}.valence", testcase.id))),
                }),
            },
            Cell {
                content: CellContent::Score(ScoreCellContent {
                    range: ScoreRange {
                        precision: 2,
                        max: Score(1.),
                        allow_partial: true,
                    },
                    key: Key(format!("testcase.{}.score", testcase.id)),
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

/// Mapping (extension, MIME type)
const STATEMENT_FORMATS: [(&str, &str); 3] = [
    ("pdf", "application/pdf"),
    ("html", "text/html"),
    ("md", "application/markdown"),
];

/// Find the statements directory, as in the italy_yaml task format
/// Searches the paths $task_dir/statement and $task_dir/testo
fn statements_dir(task_dir: &Path) -> Option<PathBuf> {
    for dir in &["statement", "testo"] {
        let dir = task_dir.join(dir);
        if dir.exists() && dir.is_dir() {
            return Some(dir);
        }
    }
    None
}

/// Tries to match the filename, returning the mimetype of the
/// matched item, if any
fn match_statement(path: &Path) -> Option<(String, FileName, MediaType)> {
    let ext = path.extension().unwrap().to_str().unwrap();
    let filename = path.file_name().unwrap().to_str().unwrap();
    let language = path.file_stem().unwrap().to_str().unwrap();
    for &(extension, mime_type) in &STATEMENT_FORMATS {
        if ext == extension {
            return Some((
                language.to_owned(),
                FileName(filename.to_owned()),
                MediaType(mime_type.to_owned()),
            ));
        }
    }
    None
}

/// find all the statements in the directory
fn statements_of(task_dir: &Path) -> Vec<FileVariant> {
    let mut result = Vec::new();
    let dir = statements_dir(task_dir);
    if let Some(dir) = dir {
        for file in dir.read_dir().unwrap() {
            let file = file.unwrap().path();
            if let Some((language, filename, mime_type)) = match_statement(&file) {
                result.push(FileVariant {
                    attributes: vec![VariantAttribute {
                        key: "language_name".to_owned(),
                        value: language,
                    }],
                    name: Some(filename),
                    r#type: Some(mime_type),
                    content: FileContent(
                        std::fs::read(file).expect("Unable to read statement file"),
                    ),
                });
            }
        }
    }
    result
}

pub fn gen_material(task: &ioi::Task) -> Material {
    Material {
        title: vec![
            TextVariant {
                attributes: vec![],
                value: task.title.clone(),
            },
            TextVariant {
                attributes: vec![VariantAttribute {
                    key: "style".to_owned(),
                    value: "short".to_owned(),
                }],
                value: task.name.clone(),
            },
        ],
        statement: statements_of(&task.path),
        attachments: files_in_dir(&task.path.join("att"))
            .map(attachment_at_path)
            .collect(),
        submission_form: submission_form(),
        awards: { subtasks_of(task).into_iter().map(award_of).collect() },
        feedback: vec![Section::Table(TableSection {
            caption: caption(),
            cols: cols(),
            row_groups: subtasks_of(task)
                .into_iter()
                .map(|subtask| row_group_of(task, subtask))
                .collect(),
        })],
    }
}
