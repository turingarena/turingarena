extern crate task_maker_cache;
extern crate task_maker_dag;
extern crate task_maker_exec;
extern crate task_maker_format;
extern crate task_maker_store;

#[macro_use]
extern crate log;

extern crate serde_json;
extern crate tempdir;

use std::path::PathBuf;
use std::sync::{
    mpsc::{self, channel},
    Arc,
};
use std::thread;

use task_maker_cache::Cache;
use task_maker_dag::CacheMode;
use task_maker_exec::{executors::LocalExecutor, ExecutorClient};
use task_maker_format::ui::UIMessage;
use task_maker_format::{ioi, EvaluationConfig, EvaluationData, TaskFormat, UISender};
use task_maker_store::*;

pub mod driver;
pub(crate) mod material;

pub fn run_task(
    task_dir: PathBuf,
    submitted_file: PathBuf,
) -> (thread::JoinHandle<()>, mpsc::IntoIter<UIMessage>) {
    let (message_tx, message_rx) = channel();
    let path = PathBuf::from(task_dir);

    let store_path = tempdir::TempDir::new("task-maker").unwrap().into_path();
    let file_store =
        Arc::new(FileStore::new(store_path.join("store")).expect("Cannot create the file store"));

    let (tx, rx_remote) = channel();
    let (tx_remote, rx) = channel();

    let server_file_store = file_store.clone();
    let server = thread::Builder::new()
        .name("Executor thread".into())
        .spawn(move || {
            let num_cores = num_cpus::get();
            let sandbox_path = store_path.join("sandboxes");
            let cache = Cache::new(store_path.join("cache")).expect("Cannot create the cache");
            let executor = LocalExecutor::new(server_file_store, num_cores, sandbox_path);

            executor.evaluate(tx_remote, rx_remote, cache).unwrap();
        })
        .expect("Failed to spawn the executor thread");

    let client = thread::Builder::new()
        .name("Client thread".into())
        .spawn(move || {
            let (mut eval, receiver) = EvaluationData::new();

            let config = eval.dag.config_mut();

            let forwarder = thread::Builder::new()
                .name("Forwarder thread".into())
                .spawn(move || {
                    for m in receiver.iter() {
                        message_tx.send(m).expect("Receiver hung-up");
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
                solution_paths: vec![submitted_file.to_owned()],
            };
            let task = ioi::Task::new(path, &eval_config).expect("Invalid task");
            task.execute(&mut eval, &eval_config)
                .expect("Failed to build the DAG");

            trace!("The DAG is: {:#?}", eval.dag);

            let ui_sender = eval.sender.clone();
            ExecutorClient::evaluate(eval.dag, tx, &rx, file_store, move |status| {
                ui_sender.send(UIMessage::ServerStatus { status })
            })
            .expect("Client failed");

            server.join().unwrap();

            drop(eval.sender);
            forwarder.join().unwrap();
        })
        .expect("Failed to spawn the executor thread");

    (client, message_rx.into_iter())
}
