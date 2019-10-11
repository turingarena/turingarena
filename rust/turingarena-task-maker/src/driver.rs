extern crate failure;

use task_maker_format::{ioi, EvaluationConfig};

use turingarena::content::*;
use turingarena::evaluation::{mem::*, record::*};
use turingarena::feedback::{table::*, *};
use turingarena::problem::{driver::*, material::*, *};
use turingarena::score::*;
use turingarena::submission::form::*;
use turingarena::submission::mem::*;

use std::convert::*;

use failure::Error;

pub struct IoiProblemDriver;

fn load_task(pack: ProblemPack) -> Result<ioi::Task, Error> {
    ioi::Task::new(
        pack.0,
        &EvaluationConfig {
            solution_filter: vec![],
            booklet_solutions: false,
        },
    )
}

impl ProblemDriver for IoiProblemDriver {
    type Error = failure::Error;
    type StatError = Self::Error;

    fn stat(pack: ProblemPack) -> Result<ProblemStat, Self::Error> {
        let task = load_task(pack)?;
        Ok(ProblemStat {
            name: ProblemName(task.name),
        })
    }

    fn gen_material(pack: ProblemPack) -> Result<Material, Self::Error> {
        let task = load_task(pack)?;
        Ok(Material {
            title: vec![TextVariant {
                attributes: vec![],
                value: task.name.clone().into(),
            }],
            statement: vec![],   // TODO
            attachments: vec![], // TODO
            submission_form: Form {
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
            },
            scored_items: {
                let mut subtasks: Vec<_> = task.subtasks.values().collect();
                subtasks.sort_by(|a, b| a.id.cmp(&b.id));
                subtasks
                    .into_iter()
                    .map(|subtask| ScoredItem {
                        title: vec![TextVariant {
                            attributes: vec![],
                            value: format!("Subtask {}", subtask.id),
                        }],
                        range: Range {
                            // TODO: assuming IOI-like tasks have integer scores
                            precision: 0,
                            max: Score(subtask.max_score),
                        },
                    })
                    .collect()
            },
            feedback: vec![Section::Table {
                caption: vec![TextVariant {
                    attributes: vec![],
                    value: format!("Test case results"),
                }],
                cols: vec![
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
                ],
                row_groups: {
                    let mut subtasks: Vec<_> = task.subtasks.values().collect();
                    subtasks.sort_by(|a, b| a.id.cmp(&b.id));
                    subtasks
                        .into_iter()
                        .map(|subtask| RowGroup {
                            title: vec![TextVariant {
                                attributes: vec![],
                                value: format!("Subtask {}", subtask.id),
                            }],
                            rows: {
                                let mut testcases: Vec<_> = subtask.testcases.values().collect();
                                testcases.sort_by(|a, b| a.id.cmp(&b.id));
                                testcases
                                    .into_iter()
                                    .map(|testcase| Row {
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
                                                    r#ref: Key(format!(
                                                        "subtask.{}.testcase.{}.score",
                                                        subtask.id, testcase.id
                                                    )),
                                                },
                                            },
                                        ],
                                    })
                                    .collect()
                            },
                        })
                        .collect()
                },
            }],
        })
    }

    fn evaluate(pack: ProblemPack, submission: Submission) -> Evaluation {
        unimplemented!()
    }
}
