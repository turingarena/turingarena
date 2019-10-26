use juniper::{FieldError, FieldResult};

use crate::*;

/// A user authorization token
#[derive(juniper::GraphQLObject)]
pub struct UserToken {
    /// The user token encoded as a JWT
    pub token: String,
}

/// dummy structure to do GraphQL queries to the contest
pub struct ContestQueries {}

#[juniper::object(Context = Context)]
impl ContestQueries {
    /// Get a user
    fn user(&self, ctx: &Context, id: Option<String>) -> FieldResult<user::User> {
        let id = if let Some(id) = &id {
            id
        } else if let Some(ctx) = &ctx.jwt_data {
            &ctx.user
        } else {
            return Err(FieldError::from("invalid authorization token"));
        };
        let user_id = user::UserId(id.to_owned());
        Ok(user::by_id(&ctx.connect_db()?, user_id)?)
    }

    /// Get the submission with the specified id
    fn submission(
        &self,
        ctx: &Context,
        submission_id: String,
    ) -> FieldResult<submission::Submission> {
        // TODO: check privilage
        Ok(submission::query(&ctx.connect_db()?, &submission_id)?)
    }

    /// Authenticate a user, generating a JWT authentication token
    fn auth(&self, ctx: &Context, token: String) -> FieldResult<Option<UserToken>> {
        Ok(auth::auth(
            &ctx.connect_db()?,
            &token,
            ctx.secret
                .as_ref()
                .ok_or(FieldError::from("Authentication disabled"))?,
        )?)
    }

    /// Current time on the server as RFC3339 date
    fn server_time(&self) -> String {
        chrono::Local::now().to_rfc3339()
    }
}
