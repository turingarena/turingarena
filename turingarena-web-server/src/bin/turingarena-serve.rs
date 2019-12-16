use structopt::StructOpt;

use turingarena_web_server::{run_server, ServerArgs};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    run_server(ServerArgs::from_args())
}
