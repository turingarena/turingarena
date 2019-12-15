use std::env;
use std::error::Error;
use std::fs::File;
use std::io::Write;
use std::path::Path;
use std::process::Command;

use graphql_client_codegen::{CodegenMode, generate_module_token_stream, GraphQLClientCodegenOptions};

use turingarena_core::contest::graphql_schema::generate_schema;

trait CheckedCommand {
    fn check(&mut self) -> Result<(), Box<dyn Error>>;
}

impl CheckedCommand for Command {
    fn check(&mut self) -> Result<(), Box<dyn Error>> {
        if !self.status().unwrap().success() {
            return Err(format!("command {:?} failed", self).into())
        }
        Ok(())
    }
}

fn main() -> Result<(), Box<dyn Error>> {
    // Unless otherwise specified, do not re-run this script
    println!("cargo:rerun-if-changed=build.rs");

    let out_dir = env::var("OUT_DIR")?;
    let out_path = Path::new(&out_dir);

    let src_dir = env::var("CARGO_MANIFEST_DIR")?;
    let src_path = Path::new(&src_dir);

    let schema_path = out_path.join("graphql-schema.json");
    let mut schema_file = File::create(&schema_path)?;

    write!(schema_file, "{}", generate_schema())?;

    let client_path = out_path.join("operations.rs");
    let mut client_file = File::create(&client_path)?;

    let operations_path = src_path
        .join("src")
        .join("operations.graphql");
    println!(
        "cargo:rerun-if-changed={}",
        operations_path.to_str().unwrap()
    );

    write!(client_file, "{}", generate_module_token_stream(
        operations_path,
        &schema_path,
        GraphQLClientCodegenOptions::new(CodegenMode::Cli),
    )?)?;

    Ok(())
}
