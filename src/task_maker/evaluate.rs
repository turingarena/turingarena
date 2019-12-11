extern crate serde_json;
extern crate tempdir;

use super::*;

use std::path::{Path, PathBuf};
use std::sync::{
    mpsc::{channel, Receiver, Sender},
    Arc,
};
use std::thread;

use task_maker_cache::Cache;
use task_maker_dag::CacheMode;
use task_maker_exec::{executors::LocalExecutor, ExecutorClient};
use task_maker_format::ui::{UIExecutionStatus, UIMessage};
use task_maker_format::{ioi, EvaluationConfig, EvaluationData, TaskFormat, UISender};
use task_maker_store::*;

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
use task_maker_format::ioi::Task;

pub fn run_evaluation<P: AsRef<Path>>(task_path: P, submission: Submission) -> Receiver<Event> {
    let task_path = task_path.as_ref().to_owned();
    let (event_tx, event_rx) = channel();

    let store_path = task_path.join(".task-maker-files");

    let min_store_size = 256 * 1024 * 1024;
    let max_store_size = 2 * min_store_size;

    let file_store = Arc::new(
        FileStore::new(store_path.join("store"), max_store_size, min_store_size)
            .expect("Cannot create the file store"),
    );

    let (tx, rx_remote) = task_maker_exec::new_local_channel();
    let (tx_remote, rx) = task_maker_exec::new_local_channel();

    let server_file_store = file_store.clone();
    thread::Builder::new()
        .name("Executor thread".into())
        .spawn(move || {
            let num_cores = num_cpus::get();
            let sandbox_path = store_path.join("sandboxes");
            let cache = Cache::new(store_path.join("cache")).expect("Cannot create the cache");
            let executor = LocalExecutor::new(server_file_store, num_cores, sandbox_path);

            executor.evaluate(tx_remote, rx_remote, cache).unwrap();
        })
        .expect("Failed to spawn the executor thread");

    thread::Builder::new()
        .name("Client thread".into())
        .spawn(move || {
            let dir = tempdir::TempDir::new("evaluation").unwrap();
            let solution_file = &submission.field_values[0].file;
            let solution_path = dir.path().join(&solution_file.name.0);
            std::fs::write(&solution_path, &solution_file.content)
                .expect("Unable to write solution file");
            println!("=={:?} start", solution_path);

            let (mut eval, receiver) = EvaluationData::new();

            let config = eval.dag.config_mut();

            let eval_config = EvaluationConfig {
                solution_filter: vec![],
                booklet_solutions: false,
                solution_paths: vec![solution_path.to_owned()],
                no_statement: true,
            };

            let task = ioi::Task::new(task_path, &eval_config).expect("Invalid task");

            // FIXME: is there a more idiomatic way to do it?
            let task2 = task.clone();

            thread::Builder::new()
                .name("Forwarder thread".into())
                .spawn(move || {
                    for m in receiver.iter() {
                        ui_message_to_events(&task2, m, &event_tx).expect("Failed to send event");
                    }
                })
                .expect("Failed to spawn the forwarder thread");

            config
                .keep_sandboxes(false)
                .dry_run(true)
                .cache_mode(CacheMode::Everything)
                .copy_exe(false)
                .extra_time(0.0);

            task.execute(&mut eval, &eval_config)
                .expect("Failed to build the DAG");

            trace!("The DAG is: {:#?}", eval.dag);

            let ui_sender = eval.sender.clone();
            ExecutorClient::evaluate(eval.dag, tx, &rx, file_store, move |status| {
                ui_sender.send(UIMessage::ServerStatus { status })
            })
            .expect("Client failed");
        })
        .expect("Failed to spawn the executor thread");
    event_rx
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
