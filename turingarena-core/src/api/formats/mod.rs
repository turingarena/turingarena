use super::*;

use crate::api::user::{User, UserInput};
use crate::data::file::FileContentInput;
use juniper::FieldResult;
use root::ApiContext;
use std::path::{PathBuf, Path};
use failure::Error;
use crate::util::archive::unpack_archive;
use tempdir::TempDir;

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
    pub archive: FileContentInput,
}

impl Import {
    pub fn load(inputs: Vec<ImportFileInput>) -> FieldResult<Import> {
        Ok(Import { archive: inputs.get(0).unwrap().content.clone() })
    }

    pub fn apply(&self, context: &ApiContext) -> FieldResult<()> {
        let temp = TempDir::new("turingarena")?;
        let archive = self.archive.decode()?;
        tar::Archive::new(&archive[..]).unpack(temp.path());

        let importer = get_importer(temp.path())?;
        importer.import(context)?;
        Ok(())
    }
}

/// Trait of an importable contest
pub trait Importable {
    /// Import into this context
    fn import(&self, context: &ApiContext) -> Result<(), Error>;
}

/// Get the importer for the specified file
pub fn get_importer(path: &Path) -> Result<Box<dyn Importable>, Error> {
    if path.join("turingarena.yaml").exists() {
        return Ok(Box::new(contest::TuringArenaImporter { path: path.into() }))
    }

    Err(failure::err_msg("Unknown import format"))
}
