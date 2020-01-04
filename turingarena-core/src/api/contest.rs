use std::fs::read;

use diesel::RunQueryDsl;
use juniper::FieldResult;

use super::*;

use crate::file::FileContentInput;
use announcements::Announcement;
use content::{FileContent, FileName, FileVariant, MediaType, TextVariant};
use contest_problem::ProblemView;
use root::ApiContext;
use root::MutationOk;

use crate::data::award::{Score, ScoreRange};
use crate::data::contest::ContestMaterial;
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

#[derive(juniper::GraphQLInputObject)]
pub struct ContestUpdateInput {
    pub archive_content: Option<FileContentInput>,
    pub start_time: Option<String>,
    pub end_time: Option<String>,
}

pub struct Contest<'a> {
    context: &'a ApiContext<'a>,
    data: ContestData,
}

impl<'a> Contest<'a> {
    pub fn new(context: &'a ApiContext<'a>) -> FieldResult<Self> {
        let data = contest::table.first(&context.database)?;
        Ok(Contest { context, data })
    }

    pub fn init(context: &'a ApiContext<'a>) -> FieldResult<()> {
        let now = chrono::Local::now();
        let configuration = ContestDataInput {
            archive_content: include_bytes!(concat!(env!("OUT_DIR"), "/initial-contest.tar.xz")),
            start_time: &now.to_rfc3339(),
            end_time: &(now + chrono::Duration::hours(4)).to_rfc3339(),
        };
        diesel::insert_into(schema::contest::table)
            .values(configuration)
            .execute(&context.database)?;
        Ok(())
    }

    pub fn update(&self, input: ContestUpdateInput) -> FieldResult<()> {
        let changeset = ContestChangeset {
            archive_content: if let Some(ref content) = input.archive_content {
                Some(content.decode()?)
            } else {
                None
            },
            start_time: input.start_time,
            end_time: input.end_time,
        };

        diesel::update(schema::contest::table)
            .set(changeset)
            .execute(&self.context.database)?;

        Ok(())
    }

    fn contest_path(&self) -> PathBuf {
        self.context
            .unpack_archive(&self.data.archive_content, "contest")
    }

    pub fn material(&self) -> FieldResult<ContestMaterial> {
        let contest_path = self.contest_path();

        Ok(ContestMaterial {
            title: contest_path
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
                .collect(),
            description: contest_path
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
                .collect(),
            resources: vec![],   // TODO
            attachments: vec![], // TODO
            start_time: self.data.start_time.clone(),
            end_time: self.data.end_time.clone(),
        })
    }
}

/// Information visible to a contestant
pub struct ContestView<'a> {
    context: &'a ApiContext<'a>,
    contest: Contest<'a>,
    user_id: Option<UserId>,
}

impl ContestView<'_> {
    pub fn new<'a>(
        context: &'a ApiContext,
        user_id: Option<UserId>,
    ) -> FieldResult<ContestView<'a>> {
        Ok(ContestView {
            context,
            contest: context.default_contest()?,
            user_id,
        })
    }

    pub fn context(&self) -> &ApiContext {
        &self.context
    }

    pub fn user_id(&self) -> &Option<UserId> {
        &self.user_id
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

    fn material(&self) -> FieldResult<ContestMaterial> {
        self.contest.material()
    }

    /// List of problems that the user can see
    fn problems(&self) -> FieldResult<Option<Vec<ProblemView>>> {
        // TODO: return only the problems that only the user can access
        Ok(Some(ProblemView::all(&self)?))
    }

    /// Range of the total score, obtained as the sum of score range of each problem
    fn total_score_range(&self) -> FieldResult<Option<ScoreRange>> {
        Ok(self.problems()?.map(|problems| {
            ScoreRange::merge(problems.iter().map(|problem| problem.total_score_range()))
        }))
    }

    /// Range of the total score, obtained as the sum of score range of each problem
    fn total_score(&self) -> FieldResult<Option<Score>> {
        let problems = self.problems()?;
        Ok(match problems {
            Some(problems) => problems
                .iter()
                .filter_map(|problem| problem.tackling())
                .map(|tackling| tackling.total_score())
                .fold(Ok(None), |a, b| -> FieldResult<_> {
                    Ok(Some(Score(a?.unwrap_or(Score(0f64)).0 + b?.0)))
                })?,
            None => None,
        })
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

    fn make_question(&self, _question: QuestionInput) -> FieldResult<MutationOk> {
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
    #[allow(dead_code)]
    id: i32,

    archive_content: Vec<u8>,

    /// Starting time of the contest, as RFC3339 date
    start_time: String,

    /// End time of the contest, as RFC3339 date
    end_time: String,
}

#[derive(Insertable)]
#[table_name = "contest"]
struct ContestDataInput<'a> {
    pub archive_content: &'a [u8],
    pub start_time: &'a str,
    pub end_time: &'a str,
}

#[derive(AsChangeset)]
#[table_name = "contest"]
struct ContestChangeset {
    pub archive_content: Option<Vec<u8>>,
    pub start_time: Option<String>,
    pub end_time: Option<String>,
}
