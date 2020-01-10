use super::*;

use crate::api::user::{User, UserInput};
use crate::data::file::FileContentInput;
use juniper::FieldResult;
use root::ApiContext;
use std::path::{PathBuf, Path};
use failure::Error;
use crate::util::archive::unpack_archive;
use tempdir::TempDir;
use crate::api::contest::ContestUpdateInput;
use crate::api::contest_problem::ProblemUpdateInput;

/// Module of various importing formats for contest
//mod italy_yaml;
mod contest;

#[derive(Debug, Clone, juniper::GraphQLInputObject)]
pub struct ImportFileInput {
    content: FileContentInput,
    name: Option<String>,
    filetype: Option<String>,
}

#[derive(Debug, Clone, juniper::GraphQLObject)]
pub struct Import {
    pub title: String,
    pub contest: ContestUpdateInput,
    pub users: Vec<UserInput>,
    pub problem: Vec<ProblemUpdateInput>,
}

impl Import {
    pub fn load(inputs: ImportFileInput) -> FieldResult<Import> {
        let temp = TempDir::new("turingarena")?;
        let archive = inputs.content.base64.decode()?;
        tar::Archive::new(&archive[..]).unpack(temp.path());

        let importer = get_importer(temp.path());
        Ok(())
    }

    pub fn apply(&self, context: &ApiContext) -> FieldResult<()> {


    }
}

/// Get the importer for the specified file
pub fn get_importer(path: &Path) -> Result<Box<dyn Into<Import>>, Error> {
    if path.join("turingarena.yaml").exists() {
        return Ok(Box::new(contest::TuringArenaImporter { path: path.into() }))
    }

    Err(failure::err_msg("Unknown import format"))
}
