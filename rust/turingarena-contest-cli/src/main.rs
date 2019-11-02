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
use juniper::InputValue;
use std::collections::HashMap;

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
    ViewContest {
    },
}

#[derive(GraphQLQuery)]
#[graphql(
    schema_path = "__generated__/graphql-schema.json",
    query_path = "src/view-contest.graphql",
    response_derives = "Debug"
)]
struct ViewContestQuery;

fn main() {
    use Command::*;
    let args = Args::from_args();

    match args.command {
        ViewContest {} => {
            let query_body: QueryBody<_> = ViewContestQuery::build_query(view_contest_query::Variables {});
            let variables_json = serde_json::to_string(&query_body.variables).unwrap();
            let variables = serde_json::from_str::<InputValue<_>>(&variables_json).unwrap();
            let schema = Schema::new(ContestQueries {}, ContestQueries {});
            let response = juniper::execute(
                &query_body.query,
                Some(query_body.operation_name),
                &schema,
                &variables.to_object_value().map(|v| v.into_iter()
                        .map(|(k, v)| (k.to_owned(), v.clone()))
                        .collect()).unwrap_or(HashMap::new()),
                &Context::default().with_args(args.contest),
            );
            println!("{:?}", response)
        }
    }
}
