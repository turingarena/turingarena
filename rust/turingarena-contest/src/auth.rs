use crate::*;
use contest::UserToken;
use diesel::SqliteConnection;
use juniper::FieldResult;
use jwt::{decode, encode, Header, Validation};
use std::error::Error;

/// Wraps a JWT User token
#[derive(juniper::GraphQLScalarValue)]
pub struct JwtToken(pub String);

/// Structure that will be encoded in the JWT
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct JwtData {
    /// Name of the user
    pub user: String,

    /// Expiraton time, as UNIX timestamp
    exp: usize,
}

/// Auth the user, generating a JWT token. Returns None if the token is not valid.
pub fn auth(conn: &SqliteConnection, token: &str, secret: &[u8]) -> FieldResult<Option<UserToken>> {
    let user = user::by_token(conn, token);
    let result = if let Ok(user) = user {
        let claims = JwtData {
            user: user.id.clone(),
            exp: 100_000_000_000_000, // TODO: generate this number as current_time + X seconds
        };
        Some(UserToken {
            token: encode(&Header::default(), &claims, &secret)?,
            user_id: Some(UserId(user.id)),
        })
    } else {
        None
    };
    Ok(result)
}

/// Validates a JWT token
pub fn validate(token: &str, secret: &[u8]) -> Result<JwtData> {
    Ok(decode(token, &secret, &Validation::default())?.claims)
}
