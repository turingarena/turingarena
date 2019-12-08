use std::fs::read;

use diesel::{ExpressionMethods, QueryResult, RunQueryDsl, SqliteConnection};
use juniper::{FieldError, FieldResult};

use super::*;

use crate::file::FileContentInput;
use announcements::Announcement;
use api::ApiContext;
use api::MutationOk;
use content::{File, FileContent, FileName, FileVariant, MediaType, Text, TextVariant};
use contest_problem::Problem;
use problem::ProblemName;
use questions::{Question, QuestionInput};
use schema::contest;
use std::path::PathBuf;
use user::{User, UserId};

/// A user authorization token
#[derive(juniper::GraphQLObject)]
pub struct UserToken {
    /// The user token encoded as a JWT
    pub token: String,
    /// The ID of the user associated with the given credentials, if any
    pub user_id: Option<UserId>,
}

/// A user authorization token
#[derive(juniper::GraphQLInputObject)]
pub struct ContestUpdateInput {
    pub archive_content: Option<FileContentInput>,
    pub start_time: Option<String>,
    pub end_time: Option<String>,
}

/// Information visible to a contestant
pub struct ContestView<'a> {
    context: &'a ApiContext<'a>,
    user_id: Option<UserId>,
    data: ContestData,
}

impl ContestView<'_> {
    pub fn new<'a>(
        context: &'a ApiContext,
        user_id: Option<UserId>,
    ) -> FieldResult<ContestView<'a>> {
        Ok(ContestView {
            context,
            data: contest::table.first(&context.database)?,
            user_id,
        })
    }

    pub fn context(&self) -> &ApiContext {
        &self.context
    }

    pub fn user_id(&self) -> &Option<UserId> {
        &self.user_id
    }

    fn contest_path(&self) -> PathBuf {
        self.context
            .unpack_archive(&self.data.archive_content, "contest")
    }
}

#[juniper_ext::graphql]
impl ContestView<'_> {
    /// The user for this contest view, if any
    fn user(&self) -> FieldResult<Option<User>> {
        let result = if let Some(user_id) = &self.user_id {
            Some(User::by_id(&self.context, user_id.clone())?)
        } else {
            None
        };
        Ok(result)
    }

    /// The contest home page
    fn home(&self) -> File {
        self.contest_path()
            .read_dir()
            .unwrap()
            .flat_map(|result| {
                let entry = result.unwrap();
                if entry.file_type().unwrap().is_dir() {
                    return None;
                }

                if let (Some(stem), Some(extension)) =
                    (entry.path().file_stem(), entry.path().extension())
                {
                    if stem != "home" {
                        return None;
                    }

                    return Some(FileVariant {
                        attributes: vec![],
                        name: Some(FileName(entry.file_name().to_str().unwrap().to_owned())),
                        content: FileContent(read(entry.path()).unwrap()),
                        r#type: match extension.to_str().unwrap() {
                            "pdf" => Some(MediaType("application/pdf".to_owned())),
                            "md" => Some(MediaType("text/markdown".to_owned())),
                            "html" => Some(MediaType("text/html".to_owned())),
                            _ => None,
                        },
                    });
                }
                None
            })
            .collect()
    }

    /// Title of the contest, as shown to the user
    fn title(&self) -> Text {
        self.contest_path()
            .read_dir()
            .unwrap()
            .flat_map(|result| {
                let entry = result.unwrap();
                if entry.file_type().unwrap().is_dir() {
                    return None;
                }

                if let (Some(stem), Some(extension)) =
                    (entry.path().file_stem(), entry.path().extension())
                {
                    if extension.to_str() != Some("txt") {
                        return None;
                    }
                    if stem.to_str() != Some("title") {
                        return None;
                    }

                    // TODO: handle multiple languages

                    return Some(TextVariant {
                        attributes: vec![],
                        value: String::from_utf8(read(entry.path()).unwrap()).unwrap(),
                    });
                }
                None
            })
            .collect()
    }

    /// A problem that the user can see
    fn problem(&self, name: ProblemName) -> FieldResult<Problem> {
        // TODO: check permissions

        Problem::by_name(&self, name)
    }

    /// List of problems that the user can see
    fn problems(&self) -> FieldResult<Option<Vec<Problem>>> {
        // TODO: return only the problems that only the user can access
        Ok(Some(Problem::all(&self)?))
    }

    /// Start time of the user participation, as RFC3339 date
    fn start_time(&self) -> FieldResult<String> {
        Ok(self.data.start_time.clone())
    }

    /// End time of the user participation, as RFC3339 date
    fn end_time(&self) -> FieldResult<String> {
        Ok(self.data.end_time.clone())
    }

    /// Questions made by the current user
    fn questions(&self) -> FieldResult<Option<Vec<Question>>> {
        if let Some(user_id) = &self.user_id {
            Ok(Some(
                questions::question_of_user(&self.context.database, user_id)?
                    .into_iter()
                    .map(|data| Question {
                        context: self.context,
                        data,
                    })
                    .collect(),
            ))
        } else {
            Ok(None)
        }
    }

    fn make_question(&self, question: QuestionInput) -> FieldResult<MutationOk> {
        unimplemented!()
    }

    /// Return a list of announcements
    fn announcements(&self) -> FieldResult<Vec<Announcement>> {
        Ok(announcements::query_all(&self.context.database)?)
    }
}

/// The configuration of a contest
#[derive(Queryable)]
pub struct ContestData {
    /// Primary key of the table. Should be *always* 0!
    id: i32,

    archive_content: Vec<u8>,

    /// Starting time of the contest, as RFC3339 date
    start_time: String,

    /// End time of the contest, as RFC3339 date
    end_time: String,
}

#[derive(Insertable)]
#[table_name = "contest"]
pub struct ContestDataInput<'a> {
    pub archive_content: &'a [u8],
    pub start_time: &'a str,
    pub end_time: &'a str,
}
