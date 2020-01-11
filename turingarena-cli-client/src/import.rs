use super::make_request;
use super::{import_contest_mutation::*, ImportContestMutation};
use failure::Error;
use graphql_client::GraphQLQuery;
use juniper::http::GraphQLRequest;
use serde::{Deserialize, Serialize};
use std::convert::TryInto;
use std::fs;
use std::path::{Path, PathBuf};
use turingarena_core::archive::pack_archive;

#[derive(Debug, Serialize, Deserialize)]
struct ContestFile {
    /// Title of the contest
    title: String,

    /// Start time of the contest
    start: Option<String>,

    /// End time of the contest
    end: Option<String>,

    /// Users of the contest
    users: Vec<ContestUser>,

    /// Problems of the contest
    problems: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize)]
struct ContestUser {
    /// Id of the user
    id: String,

    /// Name of the user
    name: String,

    /// Access token of the user
    token: String,

    /// Role of the user. Currently supported: user, admin
    role: Option<String>,
}

pub struct Importer {
    contest: ContestFile,
    path: PathBuf,
}

impl Importer {
    pub fn new<P: Into<PathBuf>>(path: P) -> Result<Self, Error> {
        let path = path.into();
        let metadata_path = path.join("turingarena.yaml");
        let metadata_data = fs::read(metadata_path)?;
        let contest = serde_yaml::from_slice::<ContestFile>(&metadata_data)?;

        Ok(Importer { contest, path })
    }

    fn contest(&self) -> ContestInput {
        let files = self.path.join("files");
        ContestInput {
            start_time: self.contest.start.as_ref().unwrap().clone(), // TODO: handle not specified date
            end_time: self.contest.end.as_ref().unwrap().clone(),
            archive_content: FileContentInput {
                base64: base64::encode(&pack_archive(files)),
            },
        }
    }

    fn problems(&self) -> Vec<ProblemInput> {
        let mut problems = Vec::new();

        for problem in &self.contest.problems {
            let path = self.path.join(problem);
            problems.push(ProblemInput {
                name: problem.clone(),
                archive_content: FileContentInput {
                    base64: base64::encode(&pack_archive(path)),
                },
            });
        }

        problems
    }

    fn users(&self) -> Vec<UserInput> {
        let mut users = Vec::new();

        for user in &self.contest.users {
            users.push(UserInput {
                id: user.id.clone(),
                token: user.token.clone(),
                display_name: user.name.clone(),
                admin: match user.role.as_ref() {
                    Some(role) => role == "admin",
                    _ => false,
                },
            });
        }

        users
    }
}

impl TryInto<GraphQLRequest> for Importer {
    type Error = Error;

    fn try_into(self) -> Result<GraphQLRequest, Self::Error> {
        let variables = Variables {
            contest: self.contest(),
            problems: self.problems(),
            users: self.users(),
        };
        Ok(make_request(ImportContestMutation::build_query, variables))
    }
}
