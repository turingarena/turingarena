extern crate dirs;
extern crate graphql_client;
extern crate reqwest;
extern crate rpassword;
extern crate serde_json;
extern crate structopt;

use structopt::StructOpt;
use graphql_client::{GraphQLQuery, QueryBody};

use serde::{Serialize, Deserialize};

use turingarena_contest::user::UserId;
use turingarena_contest::submission::SubmissionId;
use turingarena::submission::form::FieldId;
use turingarena::problem::ProblemName;
use turingarena_contest::context::Context;
use turingarena_contest::args::ContestArgs;
use turingarena_contest::Schema;
use turingarena_contest::contest::ContestQueries;
use juniper::{InputValue, DefaultScalarValue};
use std::collections::HashMap;
use juniper::http::GraphQLRequest;

macro_rules! graphql_operations {
    (
        $(
            $file:literal {
                $( $name:ident ),*
                $(,)?
            }
        ),*
        $(,)?
    ) => {
        $(
            $(
                #[derive(GraphQLQuery)]
                #[graphql(
                    schema_path = "__generated__/graphql-schema.json",
                    query_path = $file,
                    response_derives = "Debug"
                )]
                struct $name;
            )*
        )*
    }
}

graphql_operations! {
    "src/admin.graphql" {
        ViewContestQuery,
        InitDbMutation,
    },
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
}

impl Command {
    pub fn to_graphql_request(&self) -> GraphQLRequest {
        use Command::*;
        match self {
            ViewContest => {
                make_request(ViewContestQuery::build_query, view_contest_query::Variables {})
            }
            InitDb => {
                make_request(InitDbMutation::build_query, init_db_mutation::Variables {})
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
    let root_node = Schema::new(ContestQueries {}, ContestQueries {});
    let context = Context::default().with_args(args.contest).with_skip_auth(true);

    let request = args.command.to_graphql_request();
    let response = request.execute(&root_node, &context);

    println!("{}", serde_json::to_string_pretty(&response).unwrap())
}
