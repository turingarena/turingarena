use task_maker_format::ioi;
use turingarena::content::*;
use turingarena::evaluation::record::*;
use turingarena::feedback::{table::*, *};
use turingarena::problem::material::*;
use turingarena::score::*;
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

fn scored_item_of(subtask: &ioi::SubtaskInfo) -> ScoredItem {
    ScoredItem {
        title: vec![TextVariant {
            attributes: vec![],
            value: format!("Subtask {}", subtask.id),
        }],
        range: Range {
            // TODO: assuming IOI-like tasks have integer scores
            precision: 0,
            max: Score(subtask.max_score),
        },
    }
}

fn cols() -> Vec<Col> {
    vec![
        Col {
            title: vec![TextVariant {
                attributes: vec![],
                value: format!("Case"),
            }],
            content: ColContent::RowNumber,
        },
        Col {
            title: vec![TextVariant {
                attributes: vec![],
                value: format!("Score"),
            }],
            content: ColContent::Score {
                range: Range {
                    // FIXME: assuming per-test-case score has fixed precision
                    precision: 2,
                    max: Score(1.),
                },
            },
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
                content: CellContent::RowNumber(testcase.id.into()),
            },
            Cell {
                content: CellContent::Score {
                    range: Range {
                        precision: 2,
                        max: Score(1.),
                    },
                    r#ref: Key(format!("testcase.{}.score", testcase.id)),
                },
            },
        ],
    }
}

fn files_of(file_path: &std::path::PathBuf, pattern: String) -> Vec<std::path::PathBuf> {
    let path = &file_path.join(pattern);
    let mut atts = Vec::new();

    for entry in glob::glob(&path.to_string_lossy()).expect("Failed to read glob pattern") {
        atts.push(entry.unwrap().to_owned());
    }
    atts
}

fn attachments_of(file_path: std::path::PathBuf) -> Attachment {
    Attachment {
        title: vec![ TextVariant {
            attributes: vec![],
            value: file_path.file_name().unwrap().to_string_lossy().into_owned(),
        }],
        file: vec![ FileVariant {
            attributes: vec![],
            name: Some(FileName(file_path.file_name().unwrap().to_string_lossy().into_owned())),
            r#type: None,
            content: FileContent(std::fs::read(&file_path.to_string_lossy().as_ref()).unwrap()),
        }]
    }
}

fn statement_of(booklet: &ioi::Booklet) -> FileVariant {
    FileVariant {
        attributes: vec![VariantAttribute {
            key: "language".to_owned(),
            value: booklet.config().language.to_owned(),
        }],
        name: Some(FileName(booklet.dest().file_name().unwrap().to_string_lossy().into_owned())),
        r#type: Some(MediaType("application/pdf".to_owned())),
        content: FileContent(std::fs::read(booklet.dest().to_string_lossy().into_owned()).unwrap()),
    }
}

pub fn gen_material(task: &ioi::Task) -> Material {
    Material {
        title: vec![TextVariant {
            attributes: vec![],
            value: task.name.clone().into(),
        }],
        statement: task.booklets.iter().map(statement_of).collect(),
        attachments: files_of(&task.path, "att/*.*".to_owned()).into_iter().map(attachments_of).collect(),
        submission_form: submission_form(),
        scored_items: { subtasks_of(task).into_iter().map(scored_item_of).collect() },
        feedback: vec![Section::Table {
            caption: caption(),
            cols: cols(),
            row_groups: subtasks_of(task).into_iter().map(row_group_of).collect(),
        }],
    }
}
