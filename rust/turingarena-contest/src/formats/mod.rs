/// Module of various importing formats for contest
mod italy_yaml;

use crate::Context;
use std::error::Error;
use std::path::Path;

/// Result of an import
pub type ImporterResult<T> = Result<T, Box<dyn Error>>;

/// Trait that defines a contest importer
trait Importer {
    /// Constructs the importer from a file
    fn from_file(path: &Path) -> Self;

    /// Import the contest in the specified Context
    fn import(&self, context: &Context) -> ImporterResult<()>;
}

/// Imports a contest in a Context
pub fn import(context: &Context, path: &Path, format: &str) -> ImporterResult<()> {
    match format {
        "italy_yaml" => italy_yaml::ItalyYamlImporter::from_file(path).import(context),
        _ => unimplemented!("Unsupported import format {}", format),
    }
}
