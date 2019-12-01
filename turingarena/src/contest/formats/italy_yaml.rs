use std::path::{Path, PathBuf};

use chrono::{Local, TimeZone};

use problem::ProblemName;

use super::*;

use api::ApiContext;
use contest_problem;
use user;
use user::{UserId, UserInput};

use formats::ImportOperation;
/// Italy YAML contest importation format
use std::error::Error;

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
        if let Some(start) = self.start {
            context.set_start_time(Local.timestamp(start as i64, 0))?;
        }
        if let Some(end) = self.stop {
            context.set_end_time(Local.timestamp(end as i64, 0))?;
        }

        let conn = context.connect_db()?;

        for task in self.tasks {
            contest_problem::insert(&conn, ProblemName(task))?;
        }

        for user in self.users {
            user::insert(
                &conn,
                &UserInput {
                    id: user.username,
                    display_name: format!("{} {}", user.first_name, user.last_name),
                    token: user.password,
                },
            )?;
        }
        Ok(())
    }
}
