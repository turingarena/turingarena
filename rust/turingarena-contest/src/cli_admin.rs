extern crate graphql_client;
#[cfg(feature = "cli-admin-remote")]
extern crate reqwest;
extern crate rpassword;

include!(concat!(env!("OUT_DIR"), "/operations.rs"));

use graphql_client::{GraphQLQuery, QueryBody};
use juniper::{DefaultScalarValue, InputValue};
use juniper::http::GraphQLRequest;
use std::path::PathBuf;
use serde::Serialize;
use structopt::StructOpt;
use std::fs::read;

#[derive(StructOpt, Debug)]
pub enum AdminCommand {
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
