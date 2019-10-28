/// Italy YAML contest importation format
use super::{Importer, ImporterResult};
use crate::Context;
use chrono::{DateTime, Local, NaiveDateTime, TimeZone};
use std::path::{Path, PathBuf};

/// The Italy YAML contest.yaml file
#[derive(Debug, Serialize, Deserialize)]
struct ContestYaml {
    name: String,
    description: String,
    start: f64,
    stop: f64,
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
pub struct ItalyYamlImporter {
    path: PathBuf,
}

impl Importer for ItalyYamlImporter {
    fn from_file(path: &Path) -> Self {
        ItalyYamlImporter {
            path: path.to_owned(),
        }
    }

    fn import(&self, context: &Context) -> ImporterResult {
        let content = std::fs::read(&self.path)?;
        let contest_yaml = serde_yaml::from_slice::<ContestYaml>(&content)?;
        context.init_db(&contest_yaml.description)?;
        // TODO: start and end date
        for task in contest_yaml.tasks {
            context.add_problem(&task)?;
        }
        for user in contest_yaml.users {
            let display_name = format!("{} {}", user.first_name, user.last_name);
            context.add_user(&user.username, &display_name, &user.password)?;
        }
        Ok(())
    }
}
