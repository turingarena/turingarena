#![feature(decl_macro, proc_macro_hygiene)]

#[macro_use]
extern crate diesel;
extern crate juniper;
extern crate juniper_rocket;
extern crate rand;
extern crate rocket;

use diesel::prelude::*;
use juniper::{FieldError, FieldResult};

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

struct Context {}
impl juniper::Context for Context {}

impl Context {
    fn connect_db(&self) -> ConnectionResult<SqliteConnection> {
        SqliteConnection::establish("./test.sqlite")
    }
}

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

struct MutationOk;

#[juniper::object]
impl MutationOk {
    fn ok() -> bool {
        true
    }
}

struct Contest;

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

type Schema = juniper::RootNode<'static, Contest, Contest>;

use rocket::{response::content, State};

#[rocket::get("/")]
fn graphiql() -> content::Html<String> {
    juniper_rocket::graphiql_source("/graphql")
}

#[rocket::get("/graphql?<request>")]
fn get_graphql_handler(
    context: State<Context>,
    request: juniper_rocket::GraphQLRequest,
    schema: State<Schema>,
) -> juniper_rocket::GraphQLResponse {
    request.execute(&schema, &context)
}

#[rocket::post("/graphql", data = "<request>")]
fn post_graphql_handler(
    context: State<Context>,
    request: juniper_rocket::GraphQLRequest,
    schema: State<Schema>,
) -> juniper_rocket::GraphQLResponse {
    request.execute(&schema, &context)
}

fn main() {
    rocket::ignite()
        .manage(Schema::new(Contest, Contest))
        .manage(Context {})
        .mount(
            "/",
            rocket::routes![graphiql, get_graphql_handler, post_graphql_handler],
        )
        .launch();
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
