extern crate dirs;

extern crate serde_json;
extern crate structopt;

use std::collections::HashMap;
use std::path::PathBuf;

use serde::{Deserialize, Serialize};
use structopt::StructOpt;

use turingarena::{contest, problem, submission};

use problem::ProblemName;
use submission::form::FieldId;

use contest::*;
use contest::api::ApiContext;
use contest::api::ContestArgs;
use contest::contest_submission::SubmissionId;
use contest::user::{User, UserId};
use contest::graphql_schema::generate_schema;

#[derive(StructOpt, Debug)]
#[structopt(
name = "turingarena",
about = "CLI to manage the turingarena contest server"
)]
struct Args {
    #[structopt(flatten)]
    contest: ContestArgs,

    #[structopt(subcommand)]
    command: Command,
}


#[derive(StructOpt, Debug)]
enum Command {
    /// start a contest HTTP server
    #[cfg(feature = "server")]
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
    #[cfg(feature = "cli-admin")]
    Admin {
        #[structopt(subcommand)]
        command: cli_admin::AdminCommand,
    },
}

fn main() -> Result<()> {
    use Command::*;
    use api::ApiContext;
    let args = Args::from_args();
    let context = ApiContext::default().with_args(args.contest);

    match args.command {
        GenerateSchema {} => {
            generate_schema();
            Ok(())
        },
        #[cfg(feature = "server")]
        Serve {
            host,
            port,
            secret_key,
            skip_auth,
        } => {
            use contest::server::run_server;

            if skip_auth {
                eprintln!("WARNING: authentication disabled");
            } else if secret_key == None {
                eprintln!("ERROR: provide a secret OR set skip-auth");
                return Err("Secret not provided".to_owned().into());
            }
            run_server(
                host,
                port,
                context
                    .with_skip_auth(skip_auth)
                    .with_secret(secret_key.map(|s| s.as_bytes().to_owned())),
            )
        }
        #[cfg(feature = "cli-admin")]
        Admin { command } => {
            let context = context.with_skip_auth(true);
            let root_node = context.root_node();

            let request = command.to_graphql_request();
            let response = request.execute(&root_node, &context);

            println!("{}", serde_json::to_string_pretty(&response).unwrap());

            Ok(())
        }
    }
}
