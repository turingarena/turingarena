use std::path::PathBuf;
use structopt::StructOpt;

#[derive(StructOpt, Debug)]
pub struct ContestArgs {
    /// url of the database
    #[structopt(long, env = "DATABASE_URL", default_value = "./database.sqlite3")]
    pub database_url: PathBuf,

    /// path of the directory in which are contained the problems
    #[structopt(long, env = "PROBLEMS_DIR", default_value = "./")]
    pub problems_dir: PathBuf,
}

#[derive(StructOpt, Debug)]
#[structopt(
    name = "turingarena",
    about = "CLI to manage the turingarena contest server"
)]
pub struct Args {
    #[structopt(flatten)]
    pub contest: ContestArgs,

    /// command
    #[structopt(subcommand)]
    pub subcommand: Command,
}

#[derive(StructOpt, Debug)]
pub enum Command {
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
    /// generate GraphQL schema
    GenerateSchema {},
    ImportContest {
        /// Path of the contest to import
        path: PathBuf,

        /// Import format
        #[structopt(long, short, default_value = "italy_yaml")]
        format: String,

        /// Delete existing contest if already exists
        #[structopt(long)]
        force: bool,
    },
}
