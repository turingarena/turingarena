use diesel::prelude::*;
use juniper::FieldResult;

use schema::messages;

use crate::api::contest_problem::Problem;
use crate::api::root::ApiContext;
use crate::api::user::{User, UserId};

use super::*;

#[derive(Clone, Debug, Queryable)]
struct MessageData {
    id: String,
    created_at: String,
    kind: String,
    user_id: Option<String>,
    problem_name: Option<String>,
    text: String,
}

#[derive(Insertable)]
#[table_name = "messages"]
struct MessageInsertable<'a> {
    id: String,
    created_at: &'a str,
    kind: &'a str,
    user_id: Option<&'a String>,
    problem_name: Option<&'a String>,
    text: &'a str,
}

#[derive(juniper::GraphQLInputObject)]
pub struct MessageInput {
    pub kind: MessageKind,
    pub problem_name: Option<String>,
    pub user_id: Option<String>,
    pub text: String,
}

pub struct Message {
    data: MessageData,
}

#[derive(juniper::GraphQLEnum)]
pub enum MessageKind {
    Announcement,
    FromUser,
    ToUser,
}

impl Message {
    pub fn list(context: &ApiContext) -> FieldResult<Vec<Message>> {
        Ok(messages::table
            .load(&context.database)?
            .into_iter()
            .map(|data| Message { data })
            .collect())
    }

    pub fn for_user(context: &ApiContext, user_id: &Option<UserId>) -> FieldResult<Vec<Message>> {
        Ok(messages::table
            .filter(
                messages::user_id
                    .eq(user_id.as_ref().map(|id| &id.0))
                    .or(messages::user_id.is_null()),
            )
            .order(messages::created_at)
            .load(&context.database)?
            .into_iter()
            .map(|data| Message { data })
            .collect())
    }

    pub fn send(context: &ApiContext, inputs: Vec<MessageInput>) -> FieldResult<()> {
        for input in inputs {
            diesel::insert_into(messages::table)
                .values(MessageInsertable {
                    id: uuid::Uuid::new_v4().to_string(),
                    kind: match input.kind {
                        MessageKind::Announcement => "ANNOUNCEMENT",
                        MessageKind::FromUser => "FROM_USER",
                        MessageKind::ToUser => "TO_USER",
                    },
                    created_at: chrono::Local::now().to_rfc3339().as_ref(),
                    user_id: input.user_id.as_ref(),
                    problem_name: input.problem_name.as_ref(),
                    text: input.text.as_ref(),
                })
                .execute(&context.database)?;
        }
        Ok(())
    }
}

#[juniper_ext::graphql(Context = ApiContext)]
impl Message {
    pub fn id(&self) -> &String {
        &self.data.id
    }

    pub fn created_at(&self) -> &String {
        &self.data.created_at
    }

    pub fn user(&self, context: &ApiContext) -> FieldResult<Option<User>> {
        Ok(match self.data.user_id.as_ref() {
            Some(id) => Some(User::by_id(context, UserId(id.clone()))?),
            None => None,
        })
    }

    pub fn problem(&self, context: &ApiContext) -> FieldResult<Option<Problem>> {
        Ok(match self.data.problem_name.as_ref() {
            Some(name) => Some(Problem::by_name(context, name)?),
            None => None,
        })
    }

    pub fn kind(&self) -> MessageKind {
        match self.data.kind.as_ref() {
            "ANNOUNCEMENT" => MessageKind::Announcement,
            "FROM_USER" => MessageKind::FromUser,
            "TO_USER" => MessageKind::ToUser,
            _ => unreachable!(),
        }
    }

    pub fn text(&self) -> &String {
        &self.data.text
    }
}
