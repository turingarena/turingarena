use root::ApiContext;

use user;
use user::UserInput;

use super::*;

use crate::api::user::User;

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

impl Into<Import> for ContestYaml {
    fn into(self) -> Import {
        Import {
            users: self
                .users
                .into_iter()
                .map(|user| ImportUser {
                    id: user.username,
                    display_name: format!("{} {}", user.first_name, user.last_name),
                    token: user.password,
                })
                .collect(),
        }
    }
}

/// A user as in the Italy YAML contest.yaml file
#[derive(Debug, Serialize, Deserialize)]
struct ItalyYamlUser {
    first_name: String,
    last_name: String,
    username: String,
    password: String,
}

//impl ImportOperation for ContestYaml {
//    fn import_into(self, context: &ApiContext) -> ImportResult {
//        if let Some(start) = self.start {
//            context.set_start_time(Local.timestamp(start as i64, 0))?;
//        }
//        if let Some(end) = self.stop {
//            context.set_end_time(Local.timestamp(end as i64, 0))?;
//        }
//
//        contest_problem::insert(
//            &context.database,
//            self.tasks.iter().map(|name| ProblemInput {
//                name: name.to_owned(),
//                archive_content: unreachable!("TODO"),
//            }),
//        )?;
//
//        User::insert(
//            context,
//            self.users.into_iter().map(|user| UserInput {
//                id: user.username,
//                display_name: format!("{} {}", user.first_name, user.last_name),
//                token: user.password,
//            }),
//        )?;
//        Ok(())
//    }
//}
