include!(concat!(env!("OUT_DIR"), "/operations.rs"));

use graphql_client::{GraphQLQuery, QueryBody};
use juniper::http::GraphQLRequest;
use juniper::InputValue;
use serde::Serialize;
use std::fs::read;
use std::path::PathBuf;
use structopt::StructOpt;
use turingarena_core::api::root::{ApiConfig, ContestArgs};
use turingarena_core::archive::pack_archive;

#[derive(StructOpt, Debug)]
#[structopt(
    name = "turingarena-cli",
    about = "CLI to administrate a turingarena contest"
)]
pub struct CliArgs {
    #[structopt(flatten)]
    contest: ContestArgs,

    /// Command to execute
    #[structopt(subcommand)]
    command: AdminCommand,
}

#[derive(StructOpt, Debug)]
enum AdminCommand {
    ViewContest,
    InitDb,
    UpdateContest {
        #[structopt(long)]
        path: Option<String>,
        #[structopt(long)]
        start_time: Option<String>,
        #[structopt(long)]
        end_time: Option<String>,
    },
    ListUsers,
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
        #[structopt(long)]
        path: String,
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
    pub fn into_graphql_request(self) -> GraphQLRequest {
        use AdminCommand::*;
        match self {
            ViewContest => make_request(
                ViewContestQuery::build_query,
                view_contest_query::Variables {},
            ),
            InitDb => make_request(InitDbMutation::build_query, init_db_mutation::Variables {}),
            UpdateContest {
                path,
                start_time,
                end_time,
            } => make_request(
                UpdateContestMutation::build_query,
                update_contest_mutation::Variables {
                    input: update_contest_mutation::ContestUpdateInput {
                        archive_content: path.map(|path| {
                            update_contest_mutation::FileContentInput {
                                base64: base64::encode(&pack_archive(path)),
                            }
                        }),
                        start_time,
                        end_time,
                    },
                },
            ),
            ListUsers => make_request(ListUsersQuery::build_query, list_users_query::Variables {}),
            AddUser {
                id,
                display_name,
                token,
            } => make_request(
                AddUserMutation::build_query,
                add_user_mutation::Variables {
                    input: add_user_mutation::UserInput {
                        id,
                        display_name,
                        token,
                    },
                },
            ),
            DeleteUser { id } => make_request(
                DeleteUserMutation::build_query,
                delete_user_mutation::Variables { id },
            ),
            AddProblem { name, path } => make_request(
                AddProblemMutation::build_query,
                add_problem_mutation::Variables {
                    input: add_problem_mutation::ProblemInput {
                        name,
                        archive_content: add_problem_mutation::FileContentInput {
                            base64: base64::encode(&pack_archive(path)),
                        },
                    },
                },
            ),
            DeleteProblem { name } => make_request(
                DeleteProblemMutation::build_query,
                delete_problem_mutation::Variables { name },
            ),
            ImportFile { path } => {
                let content = read(&path).unwrap();
                make_request(
                    ImportMutation::build_query,
                    import_mutation::Variables {
                        input: import_mutation::ImportInput {
                            content_base64: base64::encode(&content),
                            filename: Some(path.file_name().unwrap().to_string_lossy().to_string()),
                            filetype: None,
                        },
                    },
                )
            }
        }
    }
}

fn make_request<V, B>(query_builder: B, variables: V) -> GraphQLRequest
where
    B: FnOnce(V) -> QueryBody<V>,
    V: Serialize,
{
    let query_body = query_builder(variables);

    let variables_json = serde_json::to_string(&query_body.variables).unwrap();
    let variables = serde_json::from_str::<InputValue<_>>(&variables_json).unwrap();

    GraphQLRequest::new(
        query_body.query.to_owned(),
        Some(query_body.operation_name.to_owned()),
        Some(variables),
    )
}

pub fn run_command(args: CliArgs) -> Result<(), Box<dyn std::error::Error>> {
    let config = ApiConfig::default()
        .with_args(args.contest)
        .with_skip_auth(true);

    let context = config.create_context(None);
    let root_node = context.root_node();

    let request = args.command.into_graphql_request();
    let response = request.execute(&root_node, &());

    println!("{}", serde_json::to_string_pretty(&response)?);
    Ok(())
}
