use crate::*;
use rocket::fairing::AdHoc;
use rocket::http::hyper::header::AccessControlAllowOrigin;
use rocket::http::{ContentType, Status};
use rocket::request::{self, FromRequest, Request};
use rocket::response::Response;
use rocket::response::{self, content};
use rocket::State;

use std::ffi::OsStr;
use std::io::Cursor;
use std::path::PathBuf;

#[cfg(feature = "webcontent")]
use turingarena_contest_webcontent::WebContent;

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
        .raw_header("Access-Control-Allow-Headers", "Content-Type")
        .finalize()
}

#[rocket::post("/graphql", data = "<request>")]
fn post_graphql_handler(
    request: juniper_rocket::GraphQLRequest,
    schema: State<Schema>,
    auth: Authorization,
    context: State<Context>,
) -> juniper_rocket::GraphQLResponse {
    let jwt_data = auth
        .0
        .map(|token| match auth::validate(&token, &context.secret) {
            Ok(claims) => claims,
            Err(_) => panic!("Invalid token"),
        });
    let context = context.with_jwt_data(jwt_data);
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

pub fn generate_schema() {
    let contest = Contest {
        database_url: PathBuf::from("/tmp/db.sqlite3"),
        problems_dir: PathBuf::from("/tmp"),
    };
    let (schema, _errors) = juniper::introspect(
        &Schema::new(contest::ContestQueries {}, contest::ContestMutations {}),
        &Context {
            skip_auth: false,
            jwt_data: None,
            secret: vec![],
            contest,
        },
        juniper::IntrospectionFormat::All,
    )
    .unwrap();
    println!("{}", serde_json::to_string_pretty(&schema).unwrap());
}

pub fn run_server(
    host: String,
    port: u16,
    skip_auth: bool,
    secret_key: Option<String>,
    contest: Contest,
) {
    let secret = if skip_auth {
        eprintln!("WARNING: Skipping all authentication! Use only for debugging");
        Vec::new()
    } else if secret_key == None {
        eprintln!("ERROR: You must provide a secret key OR specify --skip-auth");
        return;
    } else {
        secret_key.unwrap().as_bytes().to_owned()
    };
    let config = rocket::Config::build(rocket::config::Environment::active().unwrap())
        .port(port)
        .address(host)
        .finalize()
        .unwrap();

    rocket::custom(config)
        .manage(Schema::new(
            contest::ContestQueries {},
            contest::ContestMutations {},
        ))
        .manage(Context {
            secret,
            skip_auth,
            jwt_data: None,
            contest,
        })
        .attach(AdHoc::on_response("Cors header", |_, res| {
            res.set_header(AccessControlAllowOrigin::Any);
        }))
        .mount(
            "/",
            rocket::routes![graphiql, options_graphql, post_graphql_handler, index, dist],
        )
        .launch();
}
