use std::fs::read;

use diesel::RunQueryDsl;
use juniper::FieldResult;

use super::*;

use crate::file::FileContentInput;
use announcements::Announcement;
use content::{FileContent, FileName, FileVariant, MediaType, TextVariant};
use contest_problem::ProblemView;
use root::ApiContext;

use crate::api::award::ScoreAwardGrading;
use crate::api::contest_evaluation::Evaluation;
use crate::api::contest_problem::Problem;
use crate::data::award::{ScoreAwardDomain, ScoreAwardGrade, ScoreAwardValue, ScoreRange};
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
}

#[juniper_ext::graphql]
impl<'a> Contest<'a> {
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

    /// All the problems
    fn problems(&self) -> FieldResult<Vec<Problem>> {
        // Contestants can see problems only through `view`
        self.context.authorize_admin()?;
        Problem::all(&self.context)
    }

    /// Get the information about this contest visible to a user
    fn view(&self, user_id: Option<UserId>) -> FieldResult<ContestView> {
        self.context.authorize_user(&user_id)?;
        ContestView::new(&self, user_id)
    }

    pub fn score_range(&self) -> FieldResult<ScoreRange> {
        Ok(ScoreRange::total(
            self.problems()?.iter().map(|problem| problem.score_range()),
        ))
    }

    pub fn score_domain(&self) -> FieldResult<ScoreAwardDomain> {
        self.context.authorize_admin()?;
        Ok(ScoreAwardDomain {
            range: self.score_range()?,
        })
    }

    fn users(&self) -> FieldResult<Vec<User>> {
        self.context.authorize_admin()?;
        User::list(&self.context)
    }

    fn submissions(&self) -> FieldResult<Vec<contest_submission::Submission>> {
        self.context.authorize_admin()?;
        contest_submission::Submission::list(&self.context)
    }

    fn evaluations(&self) -> FieldResult<Vec<Evaluation>> {
        self.context.authorize_admin()?;
        Evaluation::list(&self.context)
    }
}

/// Information visible to a contestant
pub struct ContestView<'a> {
    contest: &'a Contest<'a>,
    user_id: Option<UserId>,
}

impl ContestView<'_> {
    pub fn new<'a>(
        contest: &'a Contest<'a>,
        user_id: Option<UserId>,
    ) -> FieldResult<ContestView<'a>> {
        Ok(ContestView { contest, user_id })
    }

    pub fn context(&self) -> &ApiContext {
        &self.contest.context
    }

    pub fn user_id(&self) -> &Option<UserId> {
        &self.user_id
    }

    pub fn can_view_problems() -> bool {
        true
    }
}

pub struct ProblemSet<'a> {
    contest: &'a Contest<'a>,
}

/// Set of problems currently active
#[juniper_ext::graphql]
impl ProblemSet<'_> {
    /// The list of problems
    fn problems(&self) -> FieldResult<Vec<Problem>> {
        // TODO: return only the problems that only the user can access
        Ok(Problem::all(&self.contest.context)?)
    }

    /// Range of the total score, obtained as the sum of score range of each problem
    fn score_range(&self) -> FieldResult<ScoreRange> {
        Ok(ScoreRange::total(
            self.problems()?.iter().map(|problem| problem.score_range()),
        ))
    }

    fn score_domain(&self) -> FieldResult<ScoreAwardDomain> {
        Ok(ScoreAwardDomain {
            range: self.score_range()?,
        })
    }

    /// Information about this problem set visible to a user
    fn view(&self, user_id: Option<UserId>) -> ProblemSetView {
        ProblemSetView {
            problem_set: &self,
            user_id,
        }
    }
}

pub struct ProblemSetView<'a> {
    problem_set: &'a ProblemSet<'a>,
    user_id: Option<UserId>,
}

#[juniper_ext::graphql]
impl ProblemSetView<'_> {
    fn grading(&self) -> FieldResult<ScoreAwardGrading> {
        Ok(ScoreAwardGrading {
            domain: self.problem_set.score_domain()?,
            grade: match self.tackling() {
                Some(t) => Some(t.grade()?),
                None => None,
            },
        })
    }

    /// Current progress of user in solving the problems in this problem set
    fn tackling(&self) -> Option<ProblemSetTackling> {
        // TODO: return `None` if user is not participating in the contest
        self.user_id.as_ref().map(|user_id| ProblemSetTackling {
            problem_set: &self.problem_set,
            user_id: (*user_id).clone(),
        })
    }
}

pub struct ProblemSetTackling<'a> {
    problem_set: &'a ProblemSet<'a>,
    user_id: UserId,
}

#[juniper_ext::graphql]
impl ProblemSetTackling<'_> {
    /// Total score, obtained as the sum of score of each problem
    fn score(&self) -> FieldResult<ScoreAwardValue> {
        Ok(ScoreAwardValue::total(
            self.problem_set
                .problems()?
                .iter()
                .filter_map(|problem| problem.view(Some(self.user_id.clone())).tackling())
                .map(|tackling| tackling.score())
                .collect::<FieldResult<Vec<_>>>()?,
        ))
    }

    fn grade(&self) -> FieldResult<ScoreAwardGrade> {
        Ok(ScoreAwardGrade {
            domain: self.problem_set.score_domain()?,
            value: self.score()?,
        })
    }
}

#[juniper_ext::graphql]
impl ContestView<'_> {
    fn problem_set(&self) -> Option<ProblemSet> {
        // TODO: return `None` if contest has not started yet
        Some(ProblemSet {
            contest: &self.contest,
        })
    }

    /// Questions made by the current user
    fn questions(&self) -> FieldResult<Option<Vec<Question>>> {
        if let Some(user_id) = &self.user_id {
            Ok(Some(
                questions::question_of_user(&self.context().database, user_id)?
                    .into_iter()
                    .map(|data| Question {
                        context: self.context(),
                        data,
                    })
                    .collect(),
            ))
        } else {
            Ok(None)
        }
    }

    /// Return a list of announcements
    fn announcements(&self) -> FieldResult<Vec<Announcement>> {
        Ok(announcements::query_all(&self.context().database)?)
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
