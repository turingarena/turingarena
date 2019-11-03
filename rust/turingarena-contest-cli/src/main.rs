extern crate dirs;
extern crate graphql_client;
extern crate reqwest;
extern crate rpassword;
extern crate serde_json;
extern crate structopt;

use structopt::StructOpt;
use graphql_client::{GraphQLQuery, QueryBody};

use serde::{Serialize, Deserialize};

use turingarena_contest::user::{UserId, User};
use turingarena_contest::submission::SubmissionId;
use turingarena::submission::form::FieldId;
use turingarena::problem::ProblemName;
use turingarena_contest::api::ApiContext;
use turingarena_contest::args::ContestArgs;
use juniper::{InputValue, DefaultScalarValue};
use std::collections::HashMap;
use juniper::http::GraphQLRequest;
use std::path::PathBuf;
use std::fs::read;

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

impl Command {
    pub fn to_graphql_request(self) -> GraphQLRequest {
        use Command::*;
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

fn main() {
    let args = Args::from_args();
    let context = ApiContext::default().with_args(args.contest).with_skip_auth(true);
    let root_node = context.root_node();

    let request = args.command.to_graphql_request();
    let response = request.execute(&root_node, &context);

    println!("{}", serde_json::to_string_pretty(&response).unwrap())
}
