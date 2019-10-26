extern crate serde_json;
extern crate tempdir;

use std::path::PathBuf;
use std::sync::{
    mpsc::{channel, Receiver, Sender},
    Arc,
};
use std::thread;

use task_maker_cache::Cache;
use task_maker_dag::CacheMode;
use task_maker_exec::{executors::LocalExecutor, ExecutorClient};
use task_maker_format::ui::UIMessage;
use task_maker_format::{ioi, EvaluationConfig, EvaluationData, TaskFormat, UISender};
use task_maker_store::*;

use turingarena::evaluation::{mem::*, record};
use turingarena::award::Score;
use turingarena::submission::mem::Submission;

use turingarena::evaluation::Event;

pub fn run_evaluation(task_path: PathBuf, submission: Submission) -> Receiver<Event> {
    let (event_tx, event_rx) = channel();

    let store_path = task_path.join(".task-maker-files");
    let file_store =
        Arc::new(FileStore::new(store_path.join("store")).expect("Cannot create the file store"));

    let (tx, rx_remote) = channel();
    let (tx_remote, rx) = channel();

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

            thread::Builder::new()
                .name("Forwarder thread".into())
                .spawn(move || {
                    for m in receiver.iter() {
                        ui_message_to_events(m, &event_tx).expect("Failed to send event");
                    }
                })
                .expect("Failed to spawn the forwarder thread");

            config
                .keep_sandboxes(false)
                .dry_run(true)
                .cache_mode(CacheMode::Everything)
                .copy_exe(false)
                .extra_time(0.0);

            let eval_config = EvaluationConfig {
                solution_filter: vec![],
                booklet_solutions: false,
                solution_paths: vec![solution_path.to_owned()],
            };
            let task = ioi::Task::new(task_path, &eval_config).expect("Invalid task");
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

fn ui_message_to_events(ui_message: UIMessage, tx: &Sender<Event>) -> Result<(), failure::Error> {
    match ui_message {
        UIMessage::IOITestcaseScore {
            subtask,
            testcase,
            solution,
            score,
            message,
        } => tx.send(Event::Value(ValueEvent {
            key: record::Key(format!("testcase.{}.score", testcase)),
            value: record::Value::Score(record::ScoreValue {
                score: Score(score as f64),
            }),
        }))?,
        UIMessage::IOISubtaskScore {
            subtask,
            solution,
            score,
        } => {
            tx.send(Event::Value(ValueEvent {
                key: record::Key(format!("subtask.{}.score", subtask)),
                value: record::Value::Score(record::ScoreValue {
                    score: Score(score as f64),
                }),
            }))?;
            tx.send(Event::Score(ScoreEvent {
                scorable_id: format!("subtask.{}", subtask),
                score: Score(score as f64),
            }))?;
        }
        _ => (),
    };
    Ok(())
}
