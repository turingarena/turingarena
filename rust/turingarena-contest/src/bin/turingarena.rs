/// main CLI of TuringArena
use structopt::StructOpt;
use turingarena_contest::{contest::Contest, server::run_server};

#[derive(StructOpt, Debug)]
#[structopt(
    name = "turingarena",
    about = "CLI to manage the turingarena contest server"
)]
enum Command {
    /// start a contest HTTP server
    Serve {
        /// host to bind the server to
        #[structopt(short = "H", long, default_value = "localhost")]
        host: String,

        /// port for the server to listen
        #[structopt(short, long, default_value = "8080")]
        port: u16,

        /// secret key for the webserver
        #[structopt(long, short, env = "SECRET")]
        secret_key: Option<String>,

        /// skip authentication (DANGEROUS: only for debug!)
        #[structopt(long, env = "SKIP_AUTH")]
        skip_auth: bool,
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
    DeleteUser {
        /// name of the user to remove
        username: String,
    },
    /// add a problem to the contest database
    AddProblem {
        /// name of the problem to add
        name: String,
        /// name of the problem to add
        path: String,
    },
    /// removes a problem from the contest database
    DeleteProblem {
        /// name of the problem to remove
        name: String,
    },
    /// initializes the database
    InitDb {},
}

fn main() {
    use Command::*;
    match Command::from_args() {
        Serve {
            host,
            port,
            secret_key,
            skip_auth,
        } => run_server(host, port, skip_auth, secret_key),
        InitDb {} => Contest::from_env().init_db(),
        AddUser {
            username,
            display_name,
            password,
        } => Contest::from_env().add_user(&username, &display_name, &password),
        DeleteUser { username } => Contest::from_env().delete_user(&username),
        AddProblem { name, path } => Contest::from_env().add_problem(&name, &path),
        DeleteProblem { name } => Contest::from_env().delete_problem(&name),
    }
}
