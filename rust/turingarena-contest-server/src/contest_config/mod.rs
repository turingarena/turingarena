use diesel::prelude::*;
use juniper::{FieldError, FieldResult};

use super::*;

const DDL: &str = "
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS users;
CREATE TABLE tasks (
    name TEXT PRIMARY KEY
);
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    display_name TEXT
);
";

table! {
    tasks (name) {
        name -> Text,
    }
}

#[derive(Insertable, juniper::GraphQLInputObject)]
#[table_name = "tasks"]
struct TaskInput {
    pub name: String,
}

#[derive(Queryable)]
struct Task {
    pub name: String,
}

/// A task
#[juniper::object(Context = Context)]
impl Task {
    /// Name of this task. Unique in the current contest.
    fn name(&self) -> String {
        return self.name.clone();
    }
}

table! {
    users (id) {
        id -> Text,
        display_name -> Text,
    }
}

#[derive(Insertable, juniper::GraphQLInputObject)]
#[table_name = "users"]
struct UserInput {
    pub id: Option<String>,
    pub display_name: Option<String>,
}

#[derive(Queryable)]
struct User {
    pub id: String,
    pub display_name: String,
}

/// A task
#[juniper::object(Context = Context)]
impl User {
    fn id(&self) -> String {
        return self.id.clone();
    }

    /// Name of this task. Unique in the current contest.
    fn display_name(&self) -> String {
        return self.display_name.clone();
    }
}

pub struct Contest;

#[juniper::object(Context = Context)]
impl Contest {
    fn users(context: &Context) -> FieldResult<Vec<User>> {
        // TODO: check admin credentials
        let connection = context.connect_db()?;
        return Ok(users::table.load::<User>(&connection)?);
    }

    fn tasks(context: &Context) -> FieldResult<Vec<Task>> {
        let connection = context.connect_db()?;
        return Ok(tasks::table.load::<Task>(&connection)?);
    }

    fn configure(
        context: &Context,
        tasks: Vec<TaskInput>,
        users: Vec<UserInput>,
    ) -> FieldResult<MutationOk> {
        // TODO: check admin credentials
        let connection = context.connect_db()?;
        connection
            .transaction::<_, diesel::result::Error, _>(|| {
                connection.execute(DDL)?;
                diesel::insert_into(users::table)
                    .values(
                        users
                            .into_iter()
                            .map(|u| UserInput {
                                id: u.id.or(Some(format!("user-{}", rand::random::<u64>()))),
                                ..u
                            })
                            .collect::<Vec<_>>(),
                    )
                    .execute(&connection)?;
                diesel::insert_into(tasks::table)
                    .values(tasks)
                    .execute(&connection)?;
                Ok(MutationOk)
            })
            .map_err(|e| FieldError::from(e))
    }
}
