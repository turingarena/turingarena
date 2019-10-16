/// main CLI of TuringArena

use structopt::StructOpt;
use turingarena_contest::server::run_server;
use turingarena_contest::{init_db, connect_db};
use diesel::prelude::*;
use turingarena_contest::schema;

#[derive(StructOpt, Debug)]
#[structopt(name = "turingarena", about = "CLI to manage the turingarena contest server")]
enum Command {
    /// start a contest HTTP server
    Serve {
        /// host to bind the server to
        #[structopt(short = "H", long, default_value = "localhost")]
        host: String,

        /// port for the server to listen
        #[structopt(short, long, default_value = "8080")]
        port: u16,
    },
    /// add a new user to the contest database
    AddUser {
        /// name of the user
        username: String, 

        /// display name, e.g. the full name of the user
        display_name: String, 

        /// password for the new user
        password: String,
    },
    /// removes a user from the contest database
    DeleteUser {
        /// name of the user to remove
        username: String,
    },
    /// add a problem to the contest database
    AddProblem {
        /// name of the problem to add
        name: String,
    },
    /// removes a problem from the contest database
    DeleteProblem {
        /// name of the problem to remove
        name: String,
    },
    /// initializes the database
    InitDb {

    }
}

fn main() {
    use Command::*;
    match Command::from_args() {
        Serve { host, port } => run_server(host, port),
        InitDb {} => init_db(),
        AddUser { username, display_name, password } => add_user(username, display_name, password),
        DeleteUser { username } => delete_user(username),
        AddProblem { name } => add_problem(name),
        DeleteProblem { name } => delete_problem(name),
    }
}

fn add_user(id: String, display_name: String, password: String) {
    // TODO: insert password
    use turingarena_contest::user::UserInput;
    let user = UserInput { 
        id, 
        display_name,
        password: bcrypt::hash(password, bcrypt::DEFAULT_COST).unwrap(),
    };
    let conn = connect_db().expect("cannot connect to database");
    diesel::insert_into(schema::users::table)
        .values(user)
        .execute(&conn)
        .expect("error executing user insert query");
}

fn delete_user(id: String) {
    use schema::users::dsl;
    let conn = connect_db().expect("cannot connect to database");
    diesel::delete(dsl::users.filter(dsl::id.eq(id)))
        .execute(&conn)
        .expect("error executing user delete query");
}

fn add_problem(name: String) {
    use turingarena_contest::problem::ProblemInput;
    let problem = ProblemInput { name };
    let conn = connect_db().expect("cannot connect to database");
    diesel::insert_into(schema::problems::table)
        .values(problem)
        .execute(&conn)
        .expect("error executing problem insert query");
}

fn delete_problem(name: String) {
    use schema::problems::dsl;
    let conn = connect_db().expect("cannot connect to database");
    diesel::delete(dsl::problems.filter(dsl::name.eq(name)))
        .execute(&conn)
        .expect("error executing problem delete query");
}