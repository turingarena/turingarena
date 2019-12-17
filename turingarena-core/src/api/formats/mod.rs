use super::*;

use formats::italy_yaml::ItalyYamlImporter;
use root::ApiContext;
use std::error::Error;

/// Module of various importing formats for contest
mod italy_yaml;

/// Result of an import
pub type ImportResult = Result<(), Box<dyn Error>>;

#[derive(Debug, Clone, juniper::GraphQLInputObject)]
pub struct ImportInput {
    content_base64: String,
    filename: Option<String>,
    filetype: Option<String>,
}

/// Trait that defines an file importer
trait Importer {
    type Operation: ImportOperation;
    /// Constructs the importer from a file
    fn load(
        &self,
        data: &[u8],
        filename: &Option<String>,
        filetype: &Option<String>,
    ) -> Option<Self::Operation>;

    fn load_input(&self, input: &ImportInput) -> Option<Self::Operation> {
        self.load(
            &base64::decode(&input.content_base64).ok()?,
            &input.filename,
            &input.filetype,
        )
    }
}

trait ImportOperation {
    /// Apply this importer to the contest
    fn import_into(self, context: &ApiContext) -> ImportResult;
}

/// Imports a contest in a Context
pub fn import(context: &ApiContext, input: &ImportInput) -> ImportResult {
    ItalyYamlImporter
        .load_input(input)
        .ok_or("Format not recognized")?
        .import_into(context)
}
