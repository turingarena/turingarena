use turingarena_task_maker::*;
use std::path::PathBuf;

fn main() {
    let args: Vec<_> = std::env::args().collect();
    let (server, messages) = run_task(PathBuf::from(&args[1]), PathBuf::from("sol/solution.cpp"));
    for m in messages {
        println!("{:?}", m);
    }
    server.join().unwrap();
}
