use structopt::StructOpt;
use std::error::Error;

use turingarena_core::contest::graphql_schema::run_generate_schema;
use turingarena_web_server::{ServerArgs, run_server};
use turingarena_cli_client::{CliArgs, run_command};

#[derive(StructOpt, Debug)]
#[structopt(
    name = "turingarena",
    about = "CLI to manage the turingarena contest server"
)]
enum Args {
    /// start a contest HTTP server
    Serve {
        #[structopt(flatten)]
        args: ServerArgs
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
        Args::GenerateSchema {} => {
            run_generate_schema()
        }
        Args::Serve { args } => {
            run_server(args)
        }
        Args::Admin { args } => {
            run_command(args)
        }
    }
}
