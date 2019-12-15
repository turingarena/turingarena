use structopt::StructOpt;

use turingarena_cli_client::{run_command, CliArgs};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    run_command(CliArgs::from_args())
}
