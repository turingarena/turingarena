use super::*;

use crate::api::formats::italy_yaml::ContestYaml;
use crate::api::user::{User, UserInput};
use crate::data::file::FileContentInput;
use juniper::FieldResult;
use root::ApiContext;
use std::error::Error;

/// Module of various importing formats for contest
mod italy_yaml;

#[derive(Debug, Clone, juniper::GraphQLInputObject)]
pub struct ImportFileInput {
    content: FileContentInput,
    name: Option<String>,
    filetype: Option<String>,
}

#[derive(Debug, Clone, juniper::GraphQLObject)]
pub struct ImportUser {
    pub id: String,
    pub display_name: String,
    pub token: String,
}

impl Into<UserInput> for ImportUser {
    fn into(self) -> UserInput {
        UserInput {
            id: self.id,
            display_name: self.display_name,
            token: self.token,
        }
    }
}

#[derive(Debug, Clone, juniper::GraphQLObject)]
pub struct Import {
    pub users: Vec<ImportUser>,
}

impl Import {
    pub fn load(inputs: Vec<ImportFileInput>) -> FieldResult<Import> {
        let mut users = vec![];

        for input in inputs.into_iter() {
            let mut import: Import =
                serde_yaml::from_slice::<ContestYaml>(&input.content.decode()?)?.into();
            users.append(&mut import.users);
        }

        Ok(Import { users })
    }

    pub fn apply(&self, context: &ApiContext) -> FieldResult<()> {
        User::insert(context, self.users.iter().map(|i| i.clone().into()))?;
        Ok(())
    }
}
