use turingarena_contrib_task_maker::*;

fn main() {
    let args: Vec<_> = std::env::args().collect();
    let (server, messages) = run_task(args[1].clone());
    for m in messages {
        println!("{:?}", m);
    }
    server.join().unwrap();
}
