use rand::Rng;
use std::path::{Path, PathBuf};

/// Unpacks an archive atomically.
pub fn unpack_archive<P: AsRef<Path>, T: AsRef<[u8]>>(
    workspace_path: P,
    content: T,
    prefix: &str,
) -> PathBuf {
    let workspace_path = workspace_path.as_ref().to_owned();
    let integrity = ssri::Integrity::from(content.as_ref());
    let id = integrity.to_hex().1;

    let out_path = workspace_path.join(format!("{}-{}", prefix, id));

    if !out_path.exists() {
        let temp_name_len = 8;
        let temp_name: String = std::iter::repeat(())
            .take(temp_name_len)
            .map(|()| rand::thread_rng().sample(rand::distributions::Alphanumeric))
            .collect();

        let temp_path = workspace_path.join(format!("{}-{}-{}.part", prefix, id, temp_name));

        let mut archive = tar::Archive::new(content.as_ref());
        archive.unpack(&temp_path).expect("Cannot extract archive");

        std::fs::rename(&temp_path, &out_path).expect("Cannot move extracted archive");
    }

    out_path
}

/// Creates an archive.
pub fn pack_archive<P: AsRef<Path>>(path: P) -> Vec<u8> {
    let mut archive_content = Vec::<u8>::new();

    let mut builder = tar::Builder::new(&mut archive_content);
    builder
        .append_dir_all(".", path)
        .expect("Unable to add dir to archive");
    builder.into_inner().expect("Unable to build archive");

    archive_content
}
