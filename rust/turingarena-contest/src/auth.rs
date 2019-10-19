use crate::*;
use jwt::{decode, encode, Header, Validation};
use std::error::Error;
use user::User;

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
pub fn auth(user: &User, password: &str) -> Result<String, Box<dyn Error>> {
    if bcrypt::verify(password, &user.password_bcrypt)? {
        let claims = JwtData {
            user: user.id.clone(),
            exp: 100000000000000, // TODO: generate this number as current_time + X seconds
        };
        Ok(encode(&Header::default(), &claims, secret_key().as_ref())?)
    } else {
        Err(From::from("Wrong password"))
    }
}

/// validates a JWT token
pub fn validate(token: &str) -> Result<JwtData, Box<dyn Error>> {
    Ok(decode(token, secret_key().as_ref(), &Validation::default())?.claims)
}
