use juniper::{FieldError, FieldResult};

use crate::*;
use user::User;
use problem::Problem;

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
    /// Get the view of a contest
    fn contest_view(&self, ctx: &Context, user_id: Option<String>) -> FieldResult<ContestView> {
        ctx.authorize_user(&user_id)?;
        let id = if let Some(id) = &user_id {
            id
        } else if let Some(ctx) = &ctx.jwt_data {
            &ctx.user
        } else {
            return Err(FieldError::from("invalid authorization token"));
        };
        let user_id = user::UserId(id.to_owned());
        Ok(ContestView {
            user_id: Some(user_id),
        })
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

/// A ContestView structure
pub struct ContestView {
    /// User of the current contest view
    pub user_id: Option<UserId>,
}

/// A user
#[juniper::object(Context = Context)]
impl ContestView {
    /// The user for this contest view, if any
    fn user(&self, ctx: &Context) -> FieldResult<Option<User>> {
        let result = if let Some(user_id) = &self.user_id {
            Some(user::by_id(&ctx.connect_db()?, user_id.clone())?)
        } else {
            None
        };
        Ok(result)
    }

    /// A problem that the user can see
    fn problem(&self, ctx: &Context, name: ProblemName) -> FieldResult<Problem> {
        // TODO: check permissions
        let data = problem::by_name(&ctx.connect_db()?, name)?;
        Ok(Problem {
            data,
            user_id: self.user_id.clone(),
        })
    }

    /// List of problems that the user can see
    fn problems(&self, ctx: &Context) -> FieldResult<Option<Vec<Problem>>> {
        // TODO: return only the problems that only the user can access
        let problems = problem::all(&ctx.connect_db()?)?
            .into_iter()
            .map(|p| Problem {
                data: p,
                user_id: self.user_id.clone(),
            })
            .collect();
        Ok(Some(problems))
    }

    /// Title of the contest, as shown to the user
    fn contest_title(&self, ctx: &Context) -> FieldResult<String> {
        Ok(config::current_config(&ctx.connect_db()?)?.contest_title)
    }

    /// Start time of the user participation, as RFC3339 date
    fn start_time(&self, ctx: &Context) -> FieldResult<String> {
        Ok(config::current_config(&ctx.connect_db()?)?.start_time)
    }

    /// End time of the user participation, as RFC3339 date
    fn end_time(&self, ctx: &Context) -> FieldResult<String> {
        Ok(config::current_config(&ctx.connect_db()?)?.end_time)
    }
}
