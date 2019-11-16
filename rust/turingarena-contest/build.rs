use std::env;
use std::fs::File;
use std::path::Path;
use std::process::Command;

fn main() {
    if env::var("SKIP_GRAPHQL_SCHEMA").unwrap_or("0".to_owned()) == "1" {
        return
    }

    let out_dir = env::var("OUT_DIR").unwrap();
    let out_path = Path::new(&out_dir);

    let schema_path = out_path.join("graphql-schema.json");

    let src_dir = env::var("CARGO_MANIFEST_DIR").unwrap();
    let src_path = Path::new(&src_dir);

    Command::new(env::var("CARGO").unwrap())
        .args(&[
            "install",
            "--path", src_dir.as_ref(),
            "--bin", "turingarena-graphql-schema",
            "--root", out_path.to_str().unwrap(),
            "--force",
            "--debug",
            "--offline",
            "--no-default-features",
        ])
        .env("CARGO_TARGET_DIR", out_path.join("graphql-schema-target").to_str().unwrap())
        .env("SKIP_GRAPHQL_SCHEMA", "1")
        .status()
        .unwrap();

    Command::new(env::var("CARGO").unwrap())
        .args(&[
            "install",
            "graphql_client_cli",
            "--root", out_path.to_str().unwrap(),
            "--force",
        ])
        .env("CARGO_TARGET_DIR", out_path.join("graphql-client-cli-target").to_str().unwrap())
        .status()
        .unwrap();

    let schema_file = File::create(&schema_path).unwrap();

    Command::new(out_path.join("bin").join("turingarena-graphql-schema"))
        .stdout(schema_file)
        .status()
        .unwrap();

    Command::new(out_path.join("bin").join("graphql-client"))
        .args(&[
            "generate",
            "--output-directory", out_path.to_str().unwrap(),
            "--schema-path", schema_path.to_str().unwrap(),
            src_path.join("src").join("operations.graphql").to_str().unwrap(),
        ])
        .status()
        .unwrap();
}
