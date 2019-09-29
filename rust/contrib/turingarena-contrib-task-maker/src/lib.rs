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
use std::sync::{mpsc::channel, Arc};
use std::thread;

use task_maker_cache::Cache;
use task_maker_dag::CacheMode;
use task_maker_exec::{executors::LocalExecutor, ExecutorClient};
use task_maker_format::ui::UIMessage;
use task_maker_format::{ioi, EvaluationConfig, EvaluationData, TaskFormat, UISender};
use task_maker_store::*;

pub fn run_task(p: &PathBuf) {
    let eval_config = EvaluationConfig {
        solution_filter: vec![],
        booklet_solutions: false,
    };
    let task = ioi::Task::new(p, &eval_config).expect("Invalid task");

    let (mut eval, receiver) = EvaluationData::new();
    let config = eval.dag.config_mut();

    config
        .keep_sandboxes(false)
        .dry_run(false)
        .cache_mode(CacheMode::Everything)
        .copy_exe(false)
        .extra_time(0.0);

    let ui_thread = std::thread::Builder::new()
        .name("UI".to_owned())
        .spawn(move || {
            while let Ok(message) = receiver.recv() {
                println!("{}", serde_json::to_string(&message).unwrap());
            }
        })
        .expect("Failed to spawn UI thread");

    // TODO: actually use a persistent cache
    let store_path = tempdir::TempDir::new("task-maker").unwrap().into_path();
    let file_store =
        Arc::new(FileStore::new(store_path.join("store")).expect("Cannot create the file store"));
    let cache = Cache::new(store_path.join("cache")).expect("Cannot create the cache");
    let num_cores = num_cpus::get();
    let sandbox_path = store_path.join("sandboxes");
    let executor = LocalExecutor::new(file_store.clone(), num_cores, sandbox_path);

    // build the DAG for the task
    task.execute(&mut eval, &eval_config)
        .expect("Failed to build the DAG");

    trace!("The DAG is: {:#?}", eval.dag);

    // start the server and the client
    let (tx, rx_remote) = channel();
    let (tx_remote, rx) = channel();
    let server = thread::Builder::new()
        .name("Executor thread".into())
        .spawn(move || {
            executor.evaluate(tx_remote, rx_remote, cache).unwrap();
        })
        .expect("Failed to spawn the executor thread");

    let ui_sender = eval.sender.clone();
    ExecutorClient::evaluate(eval.dag, tx, &rx, file_store, move |status| {
        ui_sender.send(UIMessage::ServerStatus { status })
    })
    .expect("Client failed");

    server.join().expect("Executor panicked");
    drop(eval.sender); // make the UI exit
    ui_thread.join().expect("UI panicked");
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
