use super::*;
use crate::api::root::ApiContext;
use crate::api::user::User;
use contest::UserToken;

use jsonwebtoken::{decode, encode, Header, Validation};
use juniper::{FieldError, FieldResult};
use juniper_ext::*;

/// Wraps a JWT User token
#[derive(GraphQLNewtype)]
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
pub fn auth(context: &ApiContext, token: &str) -> FieldResult<Option<UserToken>> {
    let secret = context
        .config
        .secret
        .as_ref()
        .ok_or_else(|| FieldError::from("Authentication disabled"))?;
    let user = User::by_token(context, token);
    let result = if let Ok(user) = user {
        let claims = JwtData {
            user: user.id().0,
            exp: 100_000_000_000_000, // TODO: generate this number as current_time + X seconds
        };
        Some(UserToken {
            token: encode(&Header::default(), &claims, &secret[..])?,
            user_id: Some(user.id()),
        })
    } else {
        None
    };
    Ok(result)
}

/// Validates a JWT token
pub fn validate(token: &str, secret: &[u8]) -> Result<JwtData, failure::Error> {
    Ok(decode(token, &secret, &Validation::default())?.claims)
}
