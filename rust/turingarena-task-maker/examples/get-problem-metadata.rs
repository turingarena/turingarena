use serde_json;
use std::env;
use std::path::PathBuf;
use task_maker_format::{ioi, EvaluationConfig};
use turingarena_task_maker::problem::*;

fn main() {
    let args: Vec<_> = env::args().collect();

    println!(
        "{}",
        serde_json::to_string_pretty(&get_problem_metadata(
            ioi::Task::new(
                PathBuf::from(&args[1]),
                &EvaluationConfig {
                    solution_filter: vec![],
                    booklet_solutions: false,
                },
            )
            .unwrap(),
        ))
        .unwrap(),
    );
}
