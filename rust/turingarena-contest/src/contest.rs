use crate::*;
use juniper::{FieldError, FieldResult};
use problem::Problem;
use schema::contest;
use user::User;

/// A user authorization token
#[derive(juniper::GraphQLObject)]
pub struct UserToken {
    /// The user token encoded as a JWT
    pub token: String,
    /// The ID of the user associated with the given credentials, if any
    pub user_id: Option<UserId>,
}

/// dummy structure to do GraphQL queries to the contest
pub struct ContestQueries {}

#[juniper::object(Context = Context)]
impl ContestQueries {
    /// Get the view of a contest
    fn contest_view(&self, ctx: &Context, user_id: Option<UserId>) -> FieldResult<ContestView> {
        ctx.authorize_user(&user_id)?;
        Ok(ContestView { user_id })
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
                .ok_or_else(|| FieldError::from("Authentication disabled"))?,
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
        Ok(current_contest(&ctx.connect_db()?)?.title)
    }

    /// Start time of the user participation, as RFC3339 date
    fn start_time(&self, ctx: &Context) -> FieldResult<String> {
        Ok(current_contest(&ctx.connect_db()?)?.start_time)
    }

    /// End time of the user participation, as RFC3339 date
    fn end_time(&self, ctx: &Context) -> FieldResult<String> {
        Ok(current_contest(&ctx.connect_db()?)?.end_time)
    }
}

/// The configuration of a contest
#[derive(Queryable)]
pub struct ContestData {
    /// Primary key of the table. Should be *always* 0!
    pub id: i32,

    /// Title of the contest, shown to the users
    pub title: String,

    /// Starting time of the contest, as RFC3339 date
    pub start_time: String,

    /// End time of the contest, as RFC3339 date
    pub end_time: String,
}

/// Get the current configuration
pub fn current_contest(conn: &SqliteConnection) -> QueryResult<ContestData> {
    contest::table.first(conn)
}

#[derive(Insertable)]
#[table_name = "contest"]
struct ContestDataInput<'a> {
    title: &'a str,
    start_time: &'a str,
    end_time: &'a str,
}

/// Create a defualt configuration
pub fn create_config(conn: &SqliteConnection, title: &str) -> QueryResult<()> {
    let now = chrono::Local::now();
    let configuration = ContestDataInput {
        title,
        start_time: &now.to_rfc3339(),
        end_time: &(now + chrono::Duration::hours(4)).to_rfc3339(),
    };
    diesel::insert_into(contest::table)
        .values(configuration)
        .execute(conn)?;
    Ok(())
}

/// Set the contest start date
pub fn set_start_time(
    conn: &SqliteConnection,
    start: chrono::DateTime<chrono::Local>,
) -> QueryResult<()> {
    diesel::update(contest::table)
        .set(contest::dsl::start_time.eq(start.to_rfc3339()))
        .execute(conn)?;
    Ok(())
}

/// Set the contest end date
pub fn set_end_time(
    conn: &SqliteConnection,
    end: chrono::DateTime<chrono::Local>,
) -> QueryResult<()> {
    diesel::update(contest::table)
        .set(contest::dsl::end_time.eq(end.to_rfc3339()))
        .execute(conn)?;
    Ok(())
}
