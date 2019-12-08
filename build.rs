use std::env;
use std::fs::{File, OpenOptions};
use std::path::Path;
use std::process::Command;

trait CheckedCommand {
    fn check(&mut self);
}

impl CheckedCommand for Command {
    fn check(&mut self) {
        if !self.status().unwrap().success() {
            panic!("command {:?} failed", self)
        }
    }
}

fn main() {
    // Unless otherwise specified, do not re-run this script
    println!("cargo:rerun-if-changed=build.rs");

    let out_dir = env::var("OUT_DIR").unwrap();
    let out_path = Path::new(&out_dir);

    let src_dir = env::var("CARGO_MANIFEST_DIR").unwrap();
    let src_path = Path::new(&src_dir);

    let schema_path = out_path.join("graphql-schema.json");

    eprintln!("ENV: {:?}", env::vars().collect::<Vec<_>>());

    if env::var_os("CARGO_FEATURE_GRAPHQL_SCHEMA").is_some() {
        Command::new(env::var("CARGO").unwrap())
            .args(&[
                "install",
                "-vv",
                "--path",
                src_dir.as_ref(),
                "--bin",
                "turingarena-graphql-schema",
                "--root",
                out_path.to_str().unwrap(),
                "--force",
                "--debug",
                "--offline",
                "--no-default-features",
                "--features",
                "contest",
            ])
            .env_clear()
            .envs(
                std::env::vars_os()
                    .filter(|(k, _)| !k.to_string_lossy().starts_with("CARGO_FEATURE_")),
            )
            .env(
                "CARGO_TARGET_DIR",
                out_path.join("graphql-schema-target").to_str().unwrap(),
            )
            .check();

        let schema_file = File::create(&schema_path).unwrap();

        Command::new(out_path.join("bin").join("turingarena-graphql-schema"))
            .stdout(schema_file)
            .check();
    }

    if env::var_os("CARGO_FEATURE_CLI_ADMIN").is_some() {
        let operations_path = src_path
            .join("src")
            .join("contest")
            .join("operations.graphql");
        println!(
            "cargo:rerun-if-changed={}",
            operations_path.to_str().unwrap()
        );

        Command::new(env::var("CARGO").unwrap())
            .args(&[
                "install",
                "-vv",
                "graphql_client_cli",
                "--root",
                out_path.to_str().unwrap(),
                "--force",
                // FIXME: should be offline
                // "--offline",
            ])
            .env(
                "CARGO_TARGET_DIR",
                out_path.join("graphql-client-cli-target").to_str().unwrap(),
            )
            .check();

        Command::new(out_path.join("bin").join("graphql-client"))
            .args(&[
                "generate",
                "--output-directory",
                out_path.to_str().unwrap(),
                "--schema-path",
                schema_path.to_str().unwrap(),
                operations_path.to_str().unwrap(),
            ])
            .check();
    }

    if env::var_os("CARGO_FEATURE_CONTEST").is_some() {
        extern crate ssri;
        extern crate tar;
        extern crate xz2;

        let initial_contest_path = src_path.join("initial-contest");

        let mut file = OpenOptions::new()
            .write(true)
            .create(true)
            .open(out_path.join("initial-contest.tar.xz"))
            .expect("Unable to open archive file");

        let mut builder = tar::Builder::new(xz2::write::XzEncoder::new(&mut file, 5));
        builder
            .append_dir_all(".", initial_contest_path)
            .expect("Unable to add dir to archive");
        builder
            .into_inner()
            .expect("Unable to build archive")
            .finish()
            .expect("Unable to build archive");
    }

    if env::var_os("CARGO_FEATURE_WEB").is_some() {
        println!("cargo:rerun-if-changed=web/");

        {
            let mut options = fs_extra::dir::CopyOptions::new();
            options.overwrite = true;
            fs_extra::dir::copy(src_path.join("web"), out_path, &options).unwrap();
        }

        let out_web_path = out_path.join("web");

        Command::new("npm")
            .current_dir(&out_web_path)
            .args(&["ci", "--ignore-scripts"])
            .check();

        std::fs::create_dir_all(&out_web_path.join("__generated__")).unwrap();

        std::fs::copy(
            &schema_path,
            &out_web_path
                .join("__generated__")
                .join("graphql-schema.json"),
        )
        .unwrap();

        Command::new("npm")
            .current_dir(&out_web_path)
            .args(&["run", "prepare"])
            .check();

        Command::new("npm")
            .current_dir(&out_web_path)
            .args(&["run", "build"])
            .check();
    }
}
