/// main CLI of TuringArena

use structopt::StructOpt;
use turingarena_contest::server::run_server;

#[derive(StructOpt, Debug)]
#[structopt(name = "turingarena", about = "CLI to manage the turingarena contest server")]
enum Command {
    /// start a contest HTTP server
    Serve {
        /// host to bind the server to
        #[structopt(short = "H", long, default_value = "localhost")]
        host: String,

        /// port for the server to listen
        #[structopt(short, long, default_value = "8080")]
        port: u16,
    },
    /// add a new user to the contest database
    AddUser {
        /// name of the user
        username: String, 

        /// display name, e.g. the full name of the user
        display_name: String, 

        /// password for the new user
        password: String,
    },
    /// removes a user from the contest database
    RemoveUser {
        /// name of the user to remove
        username: String,
    },
    /// add a task to the contest database
    AddTask {
        /// name of the task to add
        name: String,
    },
    /// removes a task from the contest database
    RemoveTask {
        /// name of the task to remove
        name: String,
    }
}

fn main() {
    use Command::*;
    match Command::from_args() {
        Serve { host, port } => run_server(host, port),
        command => unimplemented!("command {:?} not jet implemented", command),
    }
}