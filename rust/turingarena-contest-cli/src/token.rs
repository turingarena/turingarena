use std::fs;
use std::path::PathBuf;

/// returns the path of the authorization token file.
/// Creates app dir if it doen't exist
fn path() -> PathBuf {
    let app_dir = dirs::data_dir().unwrap().join("turingarena_cli");
    if !app_dir.exists() {
        fs::create_dir_all(&app_dir).unwrap();
    }
    app_dir.join("token")
}

/// reads a token from the application directory, if it exists
pub fn get() -> Option<String> {
    match fs::read_to_string(path()) {
        Ok(token) => Some(token),
        Err(_) => None,
    }
}

/// saves an authorization token to the filesystem
pub fn store(token: String) {
    fs::write(path(), token).expect("Error saving authorization token");
}

/// deletes a saved authorization token
pub fn delete() {
    fs::remove_file(path()).expect("Error removing saved token")
}
