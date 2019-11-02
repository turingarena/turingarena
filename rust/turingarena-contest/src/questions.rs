use crate::*;
use api::ApiContext;
use diesel::{ExpressionMethods, QueryDsl, QueryResult, RunQueryDsl, SqliteConnection};
use juniper::FieldResult;
use schema::{answers, questions};
use turingarena::problem::ProblemName;

/// Represents a question from a user
#[derive(Queryable, Clone, Debug)]
pub struct Question {
    id: i32,
    user_id: String,
    problem_name: Option<String>,
    time: String,
    text: String,
}

#[juniper::object(Context = ApiContext)]
impl Question {
    /// Time at which the question was inserted
    fn time(&self) -> &String {
        &self.time
    }

    /// Text of the question
    fn text(&self) -> &String {
        &self.text
    }

    /// Answer to the question, if answered
    fn answer(&self, ctx: &ApiContext) -> FieldResult<Option<Answer>> {
        Ok(answer_to(&ctx.connect_db()?, self.id)?)
    }

    /// Optionally the problem which the question refers to
    fn problem_name(&self) -> Option<ProblemName> {
        self.problem_name.clone().map(ProblemName)
    }
}

/// An input for a question
#[derive(juniper::GraphQLInputObject)]
pub struct QuestionInput {
    /// Text of the question
    text: String,

    /// Optionally the name of the problem the question refers to
    problem_name: Option<ProblemName>,
}

/// Represents an answer to a question
#[derive(Queryable, Clone, Debug)]
pub struct Answer {
    question_id: i32,
    text: String,
}

#[juniper::object]
impl Answer {
    /// Text of the answer
    fn text(&self) -> &String {
        &self.text
    }
}

/// Returns all the questions made by a user
pub fn question_of_user(
    conn: &SqliteConnection,
    user_id: &user::UserId,
) -> QueryResult<Vec<Question>> {
    questions::table
        .filter(questions::dsl::user_id.eq(&user_id.0))
        .load(conn)
}

/// Answer to the question, if present
pub fn answer_to(conn: &SqliteConnection, question_id: i32) -> QueryResult<Option<Answer>> {
    let answers = answers::table.find(question_id).load::<Answer>(conn)?;
    if answers.is_empty() {
        Ok(None)
    } else {
        Ok(Some(answers[0].clone()))
    }
}
