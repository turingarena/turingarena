extern crate dirs;
extern crate graphql_client;
extern crate reqwest;
extern crate rpassword;
extern crate serde_json;
extern crate structopt;

mod auth;
mod client;
mod submit;
mod token;
mod user;

use structopt::StructOpt;

pub static mut ENDPOINT: String = String::new();

#[derive(StructOpt, Debug)]
#[structopt(
    name = "turingarena",
    about = "CLI to manage the turingarena contest server"
)]
struct Args {
    /// TuringArena endpoint to use
    #[structopt(long, short, env = "TURINGARENA_ENDPOINT")]
    endpoint: String,

    #[structopt(subcommand)]
    command: Command,
}

#[derive(StructOpt, Debug)]
enum Command {
    /// Submit a problem to the TuringArena server
    Submit {
        /// name of the problem
        problem: String,

        /// files of the problem, in format field=path
        files: Vec<String>,
    },
    /// Login to the TuringArena server
    Login {
        /// your username
        username: String,
    },
    /// Lougout from the TuringArena server
    Logout {},
    /// Get informations about the currently logged in user
    Info {},
}

fn main() {
    use Command::*;
    let args = Args::from_args();

    unsafe {
        ENDPOINT = args.endpoint;
    }

    match args.command {
        Submit { problem, files } => submit::submit(problem, files),
        Login { username } => auth::login(username),
        Logout {} => auth::logout(),
        Info {} => user::info(),
    }
}
