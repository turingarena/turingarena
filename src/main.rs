use std::error::Error;
use structopt::StructOpt;

use turingarena_cli_client::{run_command, CliArgs};
use turingarena_core::api::graphql_schema::run_generate_schema;
use turingarena_web_server::{run_server, ServerArgs};

#[derive(StructOpt, Debug)]
#[structopt(
    name = "turingarena",
    about = "CLI to manage the turingarena contest server"
)]
enum Args {
    /// start a contest HTTP server
    Serve {
        #[structopt(flatten)]
        args: ServerArgs,
    },
    /// generate GraphQL schema
    GenerateSchema {},
    /// Administrate a turingarena contest
    Admin {
        #[structopt(flatten)]
        args: CliArgs,
    },
}

fn main() -> Result<(), Box<dyn Error>> {
    match Args::from_args() {
        Args::GenerateSchema {} => run_generate_schema(),
        Args::Serve { args } => run_server(args),
        Args::Admin { args } => run_command(args),
    }
}
