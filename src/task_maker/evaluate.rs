extern crate serde_json;
extern crate tempdir;

use super::*;

use std::path::{Path, PathBuf};
use std::sync::{
    mpsc::{channel, Receiver, Sender},
};

use task_maker_format::ui::{UIExecutionStatus, UIMessage};
use task_maker_format::ioi::Task;

use award::{AwardName, Score};
use evaluation::*;
use submission::Submission;

use crate::award::{AwardValue, BadgeAwardValue, ScoreAwardValue};
use crate::evaluation::AwardEvent;
use content::TextVariant;
use evaluation::record::ValenceValue;
use evaluation::Event;
use feedback::valence::Valence;
use rusage::{MemoryUsage, TimeUsage};
use std::process::{Command, Stdio};
use std::io::{BufReader, BufRead};
use std::env;

/// Searches for an executable in `PATH`
fn find_in_path(exe: &str) -> Option<PathBuf> {
    let path = env::var("PATH").unwrap();

    for dir in env::split_paths(&path) {
        let exe = dir.join(exe);
        if exe.exists() {
            return Some(exe);
        }
    }
    None
}

/// Searches the task-maker executable in the following locations:
/// - env variable `TASK_MAKER_EXE`
/// - executable `task-maker-rust` in `PATH`
/// - executable `task-maker` in `PATH`
fn find_task_maker() -> Result<PathBuf, failure::Error> {
    if let Ok(task_maker) = env::var("TASK_MAKER_EXE") {
        let path = PathBuf::from(task_maker);
        if path.exists() {
            return Ok(path);
        }
    }

    for name in &["task-maker-rust", "task-maker"] {
        if let Some(exe) = find_in_path(name) {
            return Ok(exe)
        }
    }

    Err(failure::err_msg("task-maker executable not found"))
}

pub fn run_evaluation<P: AsRef<Path>>(task_path: P, submission: Submission) -> Result<Receiver<Event>, failure::Error> {
    let task_path = task_path.as_ref().to_owned();
    let (event_tx, event_rx) = channel();

    // write solution to file
    let dir = tempdir::TempDir::new("evaluation")?;
    let solution_file = &submission.field_values[0].file;
    let solution_path = dir.path().join(&solution_file.name.0);
    std::fs::write(&solution_path, &solution_file.content)?;

    let mut ioi_task: Option<Task> = None;

    let mut task_maker = Command::new(find_task_maker()?);
    task_maker
        .arg("--dry-run")
        .arg("--no-statement")
        .arg("--ui=json")
        .arg("--task-dir").arg(task_path)
        .arg("--solution").arg(solution_path);

    if let Ok(args) = env::var("TASK_MAKER_ARGS") {
        task_maker.args(args.split(' '));
    }

    let mut child = task_maker
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .spawn()?;

    let stdout_reader = BufReader::new(child.stdout.as_mut().unwrap());
    for line in stdout_reader.lines() {
        let message = serde_json::from_str::<UIMessage>(&line?)?;

        // As the first message task-maker-rust sends us the task... nice!
        if let UIMessage::IOITask { task} = message {
            ioi_task = Some(task);
        } else {
            ui_message_to_events(&ioi_task.as_ref().unwrap(), message, &event_tx);
        }
    }

    child.wait()?;

    Ok(event_rx)
}

fn ui_message_to_events(
    task: &Task,
    ui_message: UIMessage,
    tx: &Sender<Event>,
) -> Result<(), failure::Error> {
    match ui_message {
        UIMessage::IOITestcaseScore {
            testcase,
            score,
            message,
            ..
        } => {
            tx.send(Event::Value(ValueEvent {
                key: record::Key(format!("testcase.{}.score", testcase)),
                value: record::Value::Score(record::ScoreValue {
                    score: Score(score as f64),
                }),
            }))?;
            tx.send(Event::Value(ValueEvent {
                key: record::Key(format!("testcase.{}.message", testcase)),
                value: record::Value::Message(record::TextValue {
                    text: vec![TextVariant {
                        value: message,
                        attributes: vec![],
                    }],
                }),
            }))?;
            tx.send(Event::Value(ValueEvent {
                key: record::Key(format!("testcase.{}.valence", testcase)),
                value: record::Value::Valence(ValenceValue {
                    valence: if score <= 0.0 {
                        Valence::Failure
                    } else if score >= 1.0 {
                        Valence::Success
                    } else {
                        Valence::Partial
                    },
                }),
            }))?;
        }
        UIMessage::IOISubtaskScore {
            subtask,
            score,
            normalized_score,
            ..
        } => {
            tx.send(Event::Value(ValueEvent {
                key: record::Key(format!("subtask.{}.score", subtask)),
                value: record::Value::Score(record::ScoreValue {
                    score: Score(score),
                }),
            }))?;
            tx.send(Event::Award(AwardEvent {
                award_name: AwardName(format!("subtask.{}.score", subtask)),
                value: AwardValue::Score(ScoreAwardValue {
                    score: Score(score),
                }),
            }))?;
            tx.send(Event::Award(AwardEvent {
                award_name: AwardName(format!("subtask.{}.badge", subtask)),
                value: AwardValue::Badge(BadgeAwardValue {
                    badge: normalized_score > 0.0,
                }),
            }))?;
        }
        UIMessage::IOIEvaluation {
            testcase, status, ..
        } => {
            if let UIExecutionStatus::Done { result } = status {
                let time_usage = result.resources.cpu_time;
                tx.send(Event::Value(ValueEvent {
                    key: record::Key(format!("testcase.{}.time_usage", testcase)),
                    value: record::Value::TimeUsage(record::TimeUsageValue {
                        time_usage: TimeUsage(time_usage),
                    }),
                }))?;
                let warning_watermark = 0.25;
                tx.send(Event::Value(ValueEvent {
                    key: record::Key(format!("testcase.{}.time_usage_valence", testcase)),
                    value: record::Value::Valence(ValenceValue {
                        valence: if task
                            .time_limit
                            .map(|limit| time_usage < limit * warning_watermark)
                            .unwrap_or(true)
                        {
                            Valence::Nominal
                        } else if task
                            .time_limit
                            .map(|limit| time_usage < limit)
                            .unwrap_or(true)
                        {
                            Valence::Warning
                        } else {
                            Valence::Failure
                        },
                    }),
                }))?;
                let memory_usage_bytes = (result.resources.memory * 1024) as f64;
                let memory_limit_bytes =
                    task.memory_limit.map(|limit| (limit * 1024 * 1024) as f64);
                tx.send(Event::Value(ValueEvent {
                    key: record::Key(format!("testcase.{}.memory_usage", testcase)),
                    value: record::Value::MemoryUsage(record::MemoryUsageValue {
                        memory_usage: MemoryUsage(memory_usage_bytes as i32),
                    }),
                }))?;
                tx.send(Event::Value(ValueEvent {
                    key: record::Key(format!("testcase.{}.memory_usage_valence", testcase)),
                    value: record::Value::Valence(ValenceValue {
                        valence: if memory_limit_bytes
                            .map(|limit| memory_usage_bytes < limit * warning_watermark)
                            .unwrap_or(true)
                        {
                            Valence::Nominal
                        } else if memory_limit_bytes
                            .map(|limit| memory_usage_bytes < limit)
                            .unwrap_or(true)
                        {
                            Valence::Warning
                        } else {
                            Valence::Failure
                        },
                    }),
                }))?;
            }
        }
        _ => (),
    };
    Ok(())
}
