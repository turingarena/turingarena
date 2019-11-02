use std::fs::read;

use diesel::{ExpressionMethods, QueryResult, RunQueryDsl, SqliteConnection};
use juniper::{FieldError, FieldResult};

use announcements::Announcement;
use api::ApiContext;
use problem::Problem;
use questions::{Question, QuestionInput};
use schema::contest;
use turingarena::content::{File, FileContent, FileName, FileVariant, MediaType, Text, TextVariant};
use turingarena::problem::ProblemName;
use user::{User, UserId};
use api::MutationOk;

use crate::*;

/// A user authorization token
#[derive(juniper::GraphQLObject)]
pub struct UserToken {
    /// The user token encoded as a JWT
    pub token: String,
    /// The ID of the user associated with the given credentials, if any
    pub user_id: Option<UserId>,
}

/// A ContestView structure
pub struct ContestView {
    /// User of the current contest view
    pub user_id: Option<UserId>,
}

/// A user
#[juniper::object(Context = ApiContext)]
impl ContestView {
    /// The user for this contest view, if any
    fn user(&self, ctx: &ApiContext) -> FieldResult<Option<User>> {
        let result = if let Some(user_id) = &self.user_id {
            Some(user::by_id(&ctx.connect_db()?, user_id.clone())?)
        } else {
            None
        };
        Ok(result)
    }

    /// The user for this contest view, if any
    fn home(&self, ctx: &ApiContext) -> File {
        ctx.problems_dir.read_dir().unwrap().flat_map(|result| {
            let entry = result.unwrap();
            if entry.file_type().unwrap().is_dir() { return None; }

            if let (Some(stem), Some(extension)) = (entry.path().file_stem(), entry.path().extension()) {
                if stem != "home" { return None; }

                return Some(FileVariant {
                    attributes: vec![],
                    name: Some(FileName(entry.file_name().to_str().unwrap().to_owned())),
                    content: FileContent(read(entry.path()).unwrap()),
                    r#type: match extension.to_str().unwrap() {
                        "pdf" => Some(MediaType("application/pdf".to_owned())),
                        "md" => Some(MediaType("text/markdown".to_owned())),
                        "html" => Some(MediaType("text/html".to_owned())),
                        _ => None
                    },
                });
            }
            None
        }).collect()
    }

    /// Title of the contest, as shown to the user
    fn title(&self, ctx: &ApiContext) -> Text {
        ctx.problems_dir.read_dir().unwrap().flat_map(|result| {
            let entry = result.unwrap();
            if entry.file_type().unwrap().is_dir() { return None; }

            if let (Some(stem), Some(extension)) = (entry.path().file_stem(), entry.path().extension()) {
                if extension.to_str() != Some("txt") { return None; }
                if stem.to_str() != Some("title") { return None; }

                // TODO: handle multiple languages

                return Some(TextVariant {
                    attributes: vec![],
                    value: String::from_utf8(read(entry.path()).unwrap()).unwrap(),
                });
            }
            None
        }).collect()
    }

    /// A problem that the user can see
    fn problem(&self, ctx: &ApiContext, name: ProblemName) -> FieldResult<Problem> {
        // TODO: check permissions
        let data = problem::by_name(&ctx.connect_db()?, name)?;
        Ok(Problem {
            data,
            user_id: self.user_id.clone(),
        })
    }

    /// List of problems that the user can see
    fn problems(&self, ctx: &ApiContext) -> FieldResult<Option<Vec<Problem>>> {
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

    /// Start time of the user participation, as RFC3339 date
    fn start_time(&self, ctx: &ApiContext) -> FieldResult<String> {
        Ok(current_contest(&ctx.connect_db()?)?.start_time)
    }

    /// End time of the user participation, as RFC3339 date
    fn end_time(&self, ctx: &ApiContext) -> FieldResult<String> {
        Ok(current_contest(&ctx.connect_db()?)?.end_time)
    }

    /// Questions made by the current user
    fn questions(&self, ctx: &ApiContext) -> FieldResult<Option<Vec<Question>>> {
        if let Some(user_id) = &self.user_id {
            Ok(Some(questions::question_of_user(
                &ctx.connect_db()?,
                user_id,
            )?))
        } else {
            Ok(None)
        }
    }

    fn make_question(&self, ctx: &ApiContext, question: QuestionInput) -> FieldResult<MutationOk> {
        unimplemented!()
    }

    /// Return a list of announcements
    fn announcements(&self, ctx: &ApiContext) -> FieldResult<Vec<Announcement>> {
        Ok(announcements::query_all(&ctx.connect_db()?)?)
    }
}

/// The configuration of a contest
#[derive(Queryable)]
pub struct ContestData {
    /// Primary key of the table. Should be *always* 0!
    pub id: i32,

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
    start_time: &'a str,
    end_time: &'a str,
}

/// Create a defualt configuration
pub fn create_config(conn: &SqliteConnection) -> QueryResult<()> {
    let now = chrono::Local::now();
    let configuration = ContestDataInput {
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
