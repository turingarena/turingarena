/// Italy YAML contest importation format
use std::error::Error;
use std::path::{Path, PathBuf};

use chrono::{Local, TimeZone};

use api::ApiContext;
use contest_problem;
use formats::ImportOperation;
use problem::ProblemName;
use user;
use user::{UserId, UserInput};

use super::*;
use crate::contest::contest_problem::ProblemInput;
use crate::contest::user::User;
use crate::file::FileContentInput;

/// The Italy YAML contest.yaml file
#[derive(Debug, Serialize, Deserialize)]
pub struct ContestYaml {
    name: String,
    description: String,
    start: Option<f64>,
    stop: Option<f64>,
    tasks: Vec<String>,
    users: Vec<ItalyYamlUser>,
}

/// A user as in the Italy YAML contest.yaml file
#[derive(Debug, Serialize, Deserialize)]
struct ItalyYamlUser {
    first_name: String,
    last_name: String,
    username: String,
    password: String,
}

/// Importer for the Italy YAML contest format
pub struct ItalyYamlImporter;

impl Importer for ItalyYamlImporter {
    type Operation = ContestYaml;
    fn load(
        &self,
        content: &[u8],
        _filename: &Option<String>,
        _filetype: &Option<String>,
    ) -> Option<ContestYaml> {
        serde_yaml::from_slice::<ContestYaml>(content).ok()
    }
}

impl ImportOperation for ContestYaml {
    fn import_into(self, context: &ApiContext) -> ImportResult {
        //        if let Some(start) = self.start {
        //            context.set_start_time(Local.timestamp(start as i64, 0))?;
        //        }
        //        if let Some(end) = self.stop {
        //            context.set_end_time(Local.timestamp(end as i64, 0))?;
        //        }

        //        contest_problem::insert(&context.database, self.tasks.iter().map(|name| ProblemInput {
        //            name: name.to_owned(),
        //            archive_content: unreachable!("TODO"),
        //        }))?;

        User::insert(
            context,
            self.users.into_iter().map(|user| UserInput {
                id: user.username,
                display_name: format!("{} {}", user.first_name, user.last_name),
                token: user.password,
            }),
        )?;
        Ok(())
    }
}
