use turingarena_contrib_task_maker::*;

fn main() {
    let args: Vec<_> = std::env::args().collect();
    let p: std::path::PathBuf = args[1].clone().into();
    run_task(&p);
}