use serde_json;
use std::env;
use problem::driver::*;
use turingarena_task_maker::driver::*;

use std::path::PathBuf;

fn main() {
    let args: Vec<_> = env::args().collect();

    println!(
        "{}",
        serde_json::to_string_pretty(
            &IoiProblemDriver::gen_material(ProblemPack(PathBuf::from(&args[1]))).unwrap()
        )
        .unwrap(),
    );
}
