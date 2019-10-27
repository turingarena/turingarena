use crate::*;
use rocket::fairing::AdHoc;
use rocket::http::hyper::header::AccessControlAllowOrigin;
use rocket::http::Status;
use rocket::request::{self, FromRequest, Request};
use rocket::response::content;
use rocket::response::Response;
use rocket::State;
use std::path::PathBuf;

#[cfg(feature = "webcontent")]
use ::{
    turingarena_contest_webcontent::WebContent,
    std::ffi::OsStr,
    std::io::Cursor,
    rocket::http::ContentType,
};

struct Authorization(Option<String>);

impl<'a, 'r> FromRequest<'a, 'r> for Authorization {
    type Error = String;

    fn from_request(request: &'a Request<'r>) -> request::Outcome<Self, Self::Error> {
        request::Outcome::Success(Authorization(
            match request.headers().get_one("Authorization") {
                Some(token) => Some(token.to_owned()),
                None => None,
            },
        ))
    }
}

#[rocket::get("/graphiql")]
fn graphiql() -> content::Html<String> {
    juniper_rocket::graphiql_source("/graphql")
}

#[rocket::options("/graphql")]
fn options_graphql<'a>() -> Response<'a> {
    Response::build()
        .raw_header("Access-Control-Allow-Origin", "*")
        .raw_header("Access-Control-Allow-Methods", "OPTIONS, POST")
        .raw_header(
            "Access-Control-Allow-Headers",
            "Content-Type, Authorization",
        )
        .finalize()
}

#[rocket::post("/graphql", data = "<request>")]
fn post_graphql_handler(
    request: juniper_rocket::GraphQLRequest,
    schema: State<Schema>,
    auth: Authorization,
    context: State<Context>,
) -> juniper_rocket::GraphQLResponse {
    let claims = context.secret.as_ref().and_then(|secret| {
        auth.0
            .and_then(|token| match auth::validate(&token, secret) {
                Ok(claims) => Some(claims),
                Err(_) => panic!("Invalid token"),
            })
    });
    let context = context.clone().with_jwt_data(claims);
    request.execute(&schema, &context)
}

#[rocket::get("/")]
fn index<'r>() -> rocket::response::Result<'r> {
    dist(Some(PathBuf::from("index.html")))
}

#[cfg(not(feature = "webcontent"))]
#[rocket::get("/<_file_option..>")]
fn dist<'r>(_file_option: Option<PathBuf>) -> rocket::response::Result<'r> {
    Err(Status::new(
        404,
        "Static files not embedded. Enable feature `webcontent`",
    ))
}

#[cfg(feature = "webcontent")]
#[rocket::get("/<file_option..>")]
fn dist<'r>(file_option: Option<PathBuf>) -> rocket::response::Result<'r> {
    let file = file_option.unwrap_or(PathBuf::new());
    let filename = file.display().to_string();
    let content = WebContent::get(&filename)
        .or(WebContent::get("index.html"))
        .unwrap();
    let ext = file
        .as_path()
        .extension()
        .and_then(OsStr::to_str)
        .unwrap_or("html");
    let content_type = ContentType::from_extension(ext)
        .ok_or(Status::new(400, "Could not get file content type"))?;
    response::Response::build()
        .header(content_type)
        .sized_body(Cursor::new(content))
        .ok()
}

pub fn generate_schema(context: Context) {
    let (schema, _errors) = juniper::introspect(
        &Schema::new(contest::ContestQueries {}, contest::ContestQueries {}),
        &context,
        juniper::IntrospectionFormat::All,
    )
    .unwrap();
    println!("{}", serde_json::to_string_pretty(&schema).unwrap());
}

pub fn run_server(host: String, port: u16, context: Context) {
    let config = rocket::Config::build(rocket::config::Environment::active().unwrap())
        .port(port)
        .address(host)
        .finalize()
        .unwrap();

    rocket::custom(config)
        .manage(Schema::new(
            contest::ContestQueries {},
            contest::ContestQueries {},
        ))
        .manage(context)
        .attach(AdHoc::on_response("Cors header", |_, res| {
            res.set_header(AccessControlAllowOrigin::Any);
        }))
        .mount(
            "/",
            rocket::routes![graphiql, options_graphql, post_graphql_handler, index, dist],
        )
        .launch();
}
