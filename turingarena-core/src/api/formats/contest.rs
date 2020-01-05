
use serde::{Serialize, Deserialize};
use std::path::{Path, PathBuf};
use std::fs;

use crate::api::user::UserInput;

const CONTEST_FILE_NAME: &str = "turingarena.yaml";

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

/// Load a contest file
fn load_contest(path: &Path) -> Result<(), failure::Error> {
    let contest = serde_yaml::from_slice::<ContestFile>(&fs::read(path)?)?;

    for user in contest.users {
        let user_input = UserInput {
            id: user.id,
            display_name: user.name,
            token: user.token,
        };
    }

    Ok(())
}

/// Search for a contest file in the current directory
/// or parent directories
fn find_contest_file(path: &Path, max_depth: u32) -> Option<PathBuf> {
    let mut dir = path;

    for _ in 0..max_depth {
        let contest = dir.join(CONTEST_FILE_NAME);
        if contest.exists() {
            return Some(contest)
        }
        dir = match dir.parent() {
            Some(dir) => dir,
            None => return None,
        }
    }

    None
}

