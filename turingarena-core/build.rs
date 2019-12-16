use std::env;
use std::fs::OpenOptions;
use std::path::Path;

fn main() {
    // Unless otherwise specified, do not re-run this script
    println!("cargo:rerun-if-changed=build.rs");

    let out_dir = env::var("OUT_DIR").unwrap();
    let out_path = Path::new(&out_dir);

    let src_dir = env::var("CARGO_MANIFEST_DIR").unwrap();
    let src_path = Path::new(&src_dir);

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
