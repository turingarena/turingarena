
use serde::{Serialize, Deserialize};
use std::path::{Path, PathBuf};
use std::fs;
use failure::Error;
use crate::api::user::{UserInput, User};
use super::Importable;
use crate::api::root::ApiContext;
use crate::api::contest_problem::{Problem, ProblemInput};
use crate::util::archive::pack_archive;
use crate::data::file::FileContentInput;
use crate::api::contest::{Contest, ContestUpdateInput};

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

/// Importer for the TuringArena format
#[derive(Debug)]
pub struct TuringArenaImporter {
    pub path: PathBuf,
}

impl TuringArenaImporter {
    fn import_contest(&self, context: &ApiContext, contest: &ContestFile) -> Result<(), Error> {
        let current = match Contest::current(context) {
            Ok(contest) => contest,
            Err(_) => {
                Contest::init(context);
                Contest::current(context).unwrap() // Juniper doesn't implement std::error::Error... fuck
            }
        };
        current.update(context, ContestUpdateInput {
            archive_content: Some(FileContentInput {
                base64: base64::encode(&pack_archive(self.path.join("files")))
            }),
            start_time: contest.start.clone(),
            end_time: contest.end.clone(),
        });
        Ok(())
    }

    fn import_tasks(&self, context: &ApiContext) -> Result<(), Error> {
        let mut problems = Vec::new();
        for dir in self.path.read_dir()? {
            let path = dir?.path();
            if path.is_dir()
                && path.file_name().unwrap() == "files"
                && !path.file_name().unwrap().to_str().unwrap().starts_with("_") {
                problems.push(ProblemInput {
                    name: path.file_name().unwrap().to_str().unwrap().into(),
                    archive_content: FileContentInput {
                        base64: base64::encode(&pack_archive(path)),
                    }
                });
            }
        }
        Problem::insert(context, problems);
        Ok(())
    }

    fn import_users(&self, context: &ApiContext, contest_users: Vec<ContestUser>) -> Result<(), Error> {
        let mut users = Vec::new();
        for user in contest_users {
            users.push(UserInput {
                id: user.id,
                display_name: user.name,
                token: user.token,
                // TODO: role: user.role,
            });
        }
        User::insert(context, users);
        Ok(())
    }
}

impl Importable for TuringArenaImporter {
    fn import(&self, context: &ApiContext) -> Result<(), Error> {
        info!("Importing contest with path = {:?}", self.path);

        let manifest = fs::read(self.path.join("turingarena.yaml"))?;
        let contest = serde_yaml::from_slice::<ContestFile>(&manifest)?;

        trace!("Contest file: {:?}", contest);

        self.import_contest(context, &contest)?;
        self.import_users(context, contest.users)?;
        self.import_tasks(context)?;
        Ok(())
    }
}

