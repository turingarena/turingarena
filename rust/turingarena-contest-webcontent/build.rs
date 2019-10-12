use std::process::Command;

fn main() {
    Command::new("npm")
        .arg("run")
        .arg("build")
        .current_dir("../../web/dist/turingarena-contest/")
        .status()
        .unwrap();
}
