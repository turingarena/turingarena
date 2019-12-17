use std::path::Path;

use failure::Error;
use task_maker_format::{EvaluationConfig, ioi};

use crate::evaluation::Evaluation;
use crate::problem::material::Material;

use super::*;

mod evaluate;
mod material;

fn load_task<P: AsRef<Path>>(path: P) -> Result<ioi::Task, Error> {
    // TODO: add option --task-info to task-maker-rust and call it here
    ioi::Task::new(
        path,
        &EvaluationConfig {
            solution_filter: vec![],
            booklet_solutions: false,
            solution_paths: vec![],
            no_statement: true,
        },
    )
}

pub fn generate_material<P: AsRef<Path>>(task_path: P) -> Result<Material, Error> {
    let task = load_task(task_path)?;
    Ok(material::generate_material(&task))
}

pub fn evaluate<P: AsRef<Path>>(
    task_path: P,
    submission: submission::Submission,
) -> evaluation::Evaluation {
    Evaluation(
        evaluate::run_evaluation(task_path, submission)
            .expect("task-maker evaluation failed"),
    )
}
