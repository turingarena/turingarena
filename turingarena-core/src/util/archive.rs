use juniper::FieldResult;
use rand::Rng;
use std::path::{Path, PathBuf};

/// Unpacks an archive atomically.
pub fn unpack_archive<P: AsRef<Path>, T: AsRef<[u8]>, F: FnOnce() -> FieldResult<T>>(
    workspace_path: P,
    prefix: &str,
    integrity: &str,
    content_provider: F,
) -> FieldResult<PathBuf> {
    let workspace_path = workspace_path.as_ref().to_owned();
    let out_path = workspace_path.join(format!("{}-{}", prefix, integrity));

    if !out_path.exists() {
        let temp_name_len = 8;
        let temp_name: String = std::iter::repeat(())
            .take(temp_name_len)
            .map(|()| rand::thread_rng().sample(rand::distributions::Alphanumeric))
            .collect();

        let temp_path = workspace_path.join(format!("{}-{}-{}.part", prefix, integrity, temp_name));

        let content = content_provider()?;

        if compute_integrity(content.as_ref()) != integrity {
            return Err("Integrity do not match".into());
        }

        let mut archive = tar::Archive::new(content.as_ref());
        archive.unpack(&temp_path)?;

        std::fs::rename(&temp_path, &out_path)?;
    }

    Ok(out_path)
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

pub fn compute_integrity(content: &[u8]) -> String {
    let integrity = ssri::Integrity::from(content.as_ref());
    integrity.to_hex().1
}
