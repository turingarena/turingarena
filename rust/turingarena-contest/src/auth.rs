use crate::*;
use user::User;
use jwt::{Header, encode, decode, Validation};

fn secret_key() -> String {
    // TODO: read secret key from a configuration file
    "test".to_owned()
}

/// structure that will be encoded in the JWT
#[derive(Serialize, Deserialize)]
pub struct JwtData {
    /// name of the user
    pub user: String,
    /// expiraton time, as UNIX timestamp
    exp: usize,
}

/// auth the user, generating a JWT token
pub fn auth(user: &User, password: &str) -> Option<String> {
    if bcrypt::verify(password, &user.password_bcrypt).unwrap() {
        let claims = JwtData {
            user: user.id.clone(),
            exp: 100000000000000, // TODO: generate this number as current_time + X seconds
        };
        Some(encode(&Header::default(), &claims, secret_key().as_ref()).unwrap())
    } else {
        None
    }
}

/// validates a JWT token
pub fn validate(token: &str) -> Result<JwtData, Box<dyn std::error::Error>> {
    Ok(decode(token, secret_key().as_ref(), &Validation::default())?.claims)
}