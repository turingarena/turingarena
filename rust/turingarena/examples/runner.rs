use std::path::PathBuf;

use problem::driver::*;
use submission::{form::*, mem::*};
use turingarena_task_maker::driver::*;

fn main() {
    let args: Vec<_> = std::env::args().collect();

    let pack = ProblemPack(PathBuf::from(&args[1]));
    let submission = Submission {
        field_values: vec![FieldValue {
            field: FieldId("solution".to_owned()),
            file: File {
                name: FileName("solution.cpp".to_owned()),
                content: std::fs::read(PathBuf::from(&args[2])).unwrap(),
            },
        }],
    };

    let evaluation = IoiProblemDriver::evaluate(pack, submission);
    for m in evaluation.0.into_iter() {
        // println!("{:?}", m);
    }
}
