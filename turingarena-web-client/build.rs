use std::env;
use std::error::Error;
use std::fs::{DirEntry, File};
use std::io::Write;
use std::path::Path;
use std::process::Command;

use turingarena_core::contest::graphql_schema::generate_schema;

trait CheckedCommand {
    fn check(&mut self) -> Result<(), Box<dyn Error>>;
}

impl CheckedCommand for Command {
    fn check(&mut self) -> Result<(), Box<dyn Error>> {
        if !self.status().unwrap().success() {
            return Err(format!("command {:?} failed", self).into());
        }
        Ok(())
    }
}

fn traverse_dir<P: AsRef<Path>, F: Fn(&DirEntry) -> () + Copy>(p: P, f: F) {
    for x in std::fs::read_dir(p).unwrap() {
        let x = x.unwrap();
        f(&x);
        if x.file_type().unwrap().is_dir() {
            traverse_dir(x.path(), f)
        }
    }
}

fn main() -> Result<(), Box<dyn Error>> {
    // Unless otherwise specified, do not re-run this script
    println!("cargo:rerun-if-changed=build.rs");

    let out_dir = env::var("OUT_DIR")?;
    let out_path = Path::new(&out_dir);

    let src_dir = env::var("CARGO_MANIFEST_DIR")?;
    let src_path = Path::new(&src_dir);

    let out_web_path = out_path.join("web");

    let build_web_env = "TURINGARENA_BUILD_WEB_CLIENT";
    println!("cargo:rerun-if-env-changed={}", build_web_env);

    if env::var_os(build_web_env).is_some() {
        traverse_dir(src_path.join("web").join("projects"), |x| {
            println!("cargo:rerun-if-changed={}", x.path().to_str().unwrap());
        });

        {
            let mut options = fs_extra::dir::CopyOptions::new();
            options.overwrite = true;
            fs_extra::dir::copy(src_path.join("web"), out_path, &options)?;
        }

        Command::new("npm")
            .current_dir(&out_web_path)
            .args(&["ci", "--ignore-scripts"])
            .check()?;

        std::fs::create_dir_all(&out_web_path.join("__generated__"))?;

        let schema_path = out_web_path
            .join("__generated__")
            .join("graphql-schema.json");
        let mut schema_file = File::create(&schema_path)?;
        write!(schema_file, "{}", generate_schema())?;

        Command::new("npm")
            .current_dir(&out_web_path)
            .args(&["run", "prepare"])
            .check()?;

        Command::new("npm")
            .current_dir(&out_web_path)
            .args(&["run", "build"])
            .check()?;
    } else {
        let dist_path = out_web_path.join("dist").join("turingarena-contest");
        let index_path = dist_path.join("index.html");
        std::fs::create_dir_all(dist_path)?;
        if !index_path.exists() {
            std::fs::copy(src_path.join("dummy-index.html"), index_path)?;
        }
    }

    Ok(())
}
