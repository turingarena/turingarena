extern crate failure;

use task_maker_format::{ioi, EvaluationConfig};

use turingarena::evaluation::mem::*;
use turingarena::problem::{driver::*, material::*, *};
use turingarena::submission::mem::*;

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
        Ok(super::material::gen_material(&task))
    }

    fn evaluate(pack: ProblemPack, submission: Submission) -> Evaluation {
        unimplemented!()
    }
}
