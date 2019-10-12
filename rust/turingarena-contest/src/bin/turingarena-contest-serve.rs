#![feature(decl_macro, proc_macro_hygiene)]

extern crate turingarena_contest_webcontent;

use rocket::{
    http::{ContentType, Status},
    response::{self, content},
    State,
};
use std::ffi::OsStr;
use std::io::Cursor;
use std::path::PathBuf;
use turingarena_contest::*;
use turingarena_contest_webcontent::WebContent;

#[rocket::get("/graphiql")]
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

#[rocket::get("/<file..>")]
fn dist<'r>(file: PathBuf) -> rocket::response::Result<'r> {
    let path = file.display().to_string();
    let filename = if path.eq("") {
        "/index.html".to_owned()
    } else {
        path
    };
    WebContent::get(&filename).map_or_else(
        || Err(Status::NotFound),
        |d| {
            let ext = file
                .as_path()
                .extension()
                .and_then(OsStr::to_str)
                .ok_or(Status::new(400, "Could not get file extension"))?;
            let content_type = ContentType::from_extension(ext)
                .ok_or(Status::new(400, "Could not get file content type"))?;
            response::Response::build()
                .header(content_type)
                .sized_body(Cursor::new(d))
                .ok()
        },
    )
}

fn main() {
    rocket::ignite()
        .manage(Schema::new(contest::Contest, contest::Contest))
        .manage(Context {})
        .mount(
            "/",
            rocket::routes![graphiql, get_graphql_handler, post_graphql_handler, dist],
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
