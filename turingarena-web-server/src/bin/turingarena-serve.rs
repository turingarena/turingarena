use structopt::StructOpt;

use turingarena_web_server::{ServerArgs, run_server};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    run_server(ServerArgs::from_args())
}