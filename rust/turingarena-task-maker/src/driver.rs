extern crate failure;

use std::fs;

use task_maker_format::{ioi, EvaluationConfig};

use turingarena::evaluation::mem::*;
use turingarena::problem::{driver::*, material::*, *};
use turingarena::submission::mem::*;

use failure::Error;
use crate::run_task;

pub struct IoiProblemDriver;

fn load_task(pack: ProblemPack) -> Result<ioi::Task, Error> {
    ioi::Task::new(
        pack.0,
        &EvaluationConfig {
            solution_filter: vec![],
            booklet_solutions: false,
            solution_paths: vec![],
        },
    )
}

// impl ProblemDriver for IoiProblemDriver {
//     type Error = failure::Error;
//     type StatError = Self::Error;

//     fn stat(pack: ProblemPack) -> Result<ProblemStat, Self::Error> {
//         let task = load_task(pack)?;
//         Ok(ProblemStat {
//             name: ProblemName(task.name),
//         })
//     }

//     fn gen_material(pack: ProblemPack) -> Result<Material, Self::Error> {
//         let task = load_task(pack)?;
//         Ok(super::material::gen_material(&task))
//     }

//     fn evaluate(pack: ProblemPack, submission: Submission) -> Evaluation {
//         let file = submission.field_values[0].file; 
//         let filename = file.name.0;
//         let tmpdir = tempdir::TempDir::new("turingarena")
//             .expect("Cannot create temporary directory");
//         let solution = tmpdir.path().join(filename);
//         fs::write(solution, file.content)
//             .expect("Cannot write submission file");

//         run_task(pack.0, solution);
//     }
// }
