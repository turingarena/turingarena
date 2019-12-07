extern crate failure;

use super::*;

use failure::Error;
use task_maker_format::{ioi, EvaluationConfig};

use crate::evaluation::Evaluation;
use crate::problem::driver::ProblemDriver;
use crate::problem::material::Material;
use crate::problem::ProblemName;
use crate::submission::Submission;
use evaluation::*;
use problem::{driver::*, material::*, *};
use std::path::{Path, PathBuf};
use submission::*;

pub struct IoiProblemDriver;

fn load_task<P: AsRef<Path>>(path: P) -> Result<ioi::Task, Error> {
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

impl ProblemDriver for IoiProblemDriver {
    type Error = failure::Error;

    fn generate_material<P: AsRef<Path>>(task_path: P) -> Result<Material, Self::Error> {
        let task = load_task(task_path)?;
        Ok(super::material::generate_material(&task))
    }

    fn evaluate<P: AsRef<Path>>(
        task_path: P,
        submission: submission::Submission,
    ) -> evaluation::Evaluation {
        Evaluation(super::evaluate::run_evaluation(task_path, submission))
    }
}
