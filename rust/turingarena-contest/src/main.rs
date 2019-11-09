extern crate dirs;
extern crate graphql_client;
extern crate reqwest;
extern crate rpassword;
extern crate serde_json;
extern crate structopt;

use std::collections::HashMap;
use std::fs::read;
use std::path::PathBuf;

use graphql_client::{GraphQLQuery, QueryBody};
use juniper::{DefaultScalarValue, InputValue};
use juniper::http::GraphQLRequest;
use serde::{Deserialize, Serialize};
use structopt::StructOpt;

use turingarena::problem::ProblemName;
use turingarena::submission::form::FieldId;
use turingarena_contest::*;
use turingarena_contest::api::ApiContext;
use turingarena_contest::api::ContestArgs;
use turingarena_contest::server::run_server;
use turingarena_contest::submission::SubmissionId;
use turingarena_contest::user::{User, UserId};

macro_rules! graphql_operations {
    (
        $( $name:ident : $file: literal ),*
        $(,)?
    ) => {
        $(
            #[derive(GraphQLQuery)]
            #[graphql(
                schema_path = "__generated__/graphql-schema.json",
                query_path = $file,
                response_derives = "Debug"
            )]
            struct $name;
        )*
    }
}

graphql_operations! {
    InitDbMutation: "src/graphql/InitDbMutation.graphql",
    ViewContestQuery: "src/graphql/ViewContestQuery.graphql",
    AddUserMutation: "src/graphql/AddUserMutation.graphql",
    DeleteUserMutation: "src/graphql/DeleteUserMutation.graphql",
    AddProblemMutation: "src/graphql/AddProblemMutation.graphql",
    DeleteProblemMutation: "src/graphql/DeleteProblemMutation.graphql",
    ImportMutation: "src/graphql/ImportMutation.graphql",
}

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
    Admin {
        #[structopt(subcommand)]
        command: AdminCommand,
    },
}

#[derive(StructOpt, Debug)]
enum AdminCommand {
    ViewContest,
    InitDb,
    AddUser {
        #[structopt(long)]
        id: String,
        #[structopt(long)]
        display_name: String,
        #[structopt(long)]
        token: String,
    },
    DeleteUser {
        id: String,
    },
    AddProblem {
        #[structopt(long)]
        name: String,
    },
    DeleteProblem {
        name: String,
    },
    ImportFile {
        /// Path of the contest to import
        path: PathBuf,
    },

}

impl AdminCommand {
    pub fn to_graphql_request(self) -> GraphQLRequest {
        use AdminCommand::*;
        match self {
            ViewContest => make_request(ViewContestQuery::build_query, view_contest_query::Variables {}),
            InitDb => make_request(InitDbMutation::build_query, init_db_mutation::Variables {}),
            AddUser {
                id, display_name, token
            } => make_request(AddUserMutation::build_query, add_user_mutation::Variables {
                input: add_user_mutation::UserInput {
                    id,
                    display_name,
                    token,
                },
            }),
            DeleteUser { id } => make_request(DeleteUserMutation::build_query, delete_user_mutation::Variables {
                id
            }),
            AddProblem { name } => make_request(AddProblemMutation::build_query, add_problem_mutation::Variables {
                name
            }),
            DeleteProblem { name } => make_request(DeleteProblemMutation::build_query, delete_problem_mutation::Variables {
                name
            }),
            ImportFile { path } => {
                let content = read(&path).unwrap();
                make_request(ImportMutation::build_query, import_mutation::Variables {
                    input: import_mutation::ImportInput {
                        content_base64: base64::encode(&content),
                        filename: Some(path.file_name().unwrap().to_string_lossy().to_string()),
                        filetype: None,
                    },
                })
            }
        }
    }
}

fn make_request<V, B>(query_builder: B, variables: V) -> GraphQLRequest
    where B: FnOnce(V) -> QueryBody<V>,
          V: Serialize {
    let query_body = query_builder(variables);

    let variables_json = serde_json::to_string(&query_body.variables).unwrap();
    let variables = serde_json::from_str::<InputValue<_>>(&variables_json).unwrap();

    GraphQLRequest::new(
        query_body.query.to_owned(),
        Some(query_body.operation_name.to_owned()),
        Some(variables),
    )
}

fn main() -> Result<()> {
    use Command::*;
    use api::ApiContext;
    use server::{generate_schema, run_server};

    let args = Args::from_args();
    let context = ApiContext::default().with_args(args.contest);

    match args.command {
        GenerateSchema {} => generate_schema(context),
        Serve {
            host,
            port,
            secret_key,
            skip_auth,
        } => {
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
        },
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
