use juniper::{FieldError, FieldResult};

use crate::*;
use problem::*;
use schema::{problems, users};

#[derive(Clone)]
pub struct Contest {
    database_url: String,
}

/// a user authorization token
#[derive(juniper::GraphQLObject)]
pub struct UserToken {
    token: String,
}

type Result<T> = std::result::Result<T, Box<dyn std::error::Error>>;

impl Contest {
    pub fn from_env() -> Contest {
        let database_url = std::env::var("DATABASE_URL").unwrap_or("./database.sqlite3".to_owned());
        Contest::with_database(&database_url)
    }

    pub fn with_database(database_url: &str) -> Contest {
        Contest {
            database_url: database_url.to_owned(),
        }
    }

    pub fn connect_db(&self) -> ConnectionResult<SqliteConnection> {
        SqliteConnection::establish(&self.database_url)
    }

    pub fn init_db(&self) {
        let connection = self.connect_db().expect("Error connecting to the database");
        embedded_migrations::run_with_output(&connection, &mut std::io::stdout())
            .expect("Error while initializing the database");
    }

    pub fn add_user(&self, id: &str, display_name: &str, password: &str) {
        use crate::user::UserInput;
        let user = UserInput {
            id: id.to_owned(),
            display_name: display_name.to_owned(),
            password_bcrypt: bcrypt::hash(password, bcrypt::DEFAULT_COST).unwrap(),
        };
        let conn = self.connect_db().expect("cannot connect to database");
        diesel::insert_into(schema::users::table)
            .values(user)
            .execute(&conn)
            .expect("error executing user insert query");
    }

    pub fn delete_user(&self, id: &str) {
        use schema::users::dsl;
        let conn = self.connect_db().expect("cannot connect to database");
        diesel::delete(dsl::users.filter(dsl::id.eq(id)))
            .execute(&conn)
            .expect("error executing user delete query");
    }

    pub fn get_user(&self, id: &str) -> Result<user::User> {
        Ok(users::table.find(id).first(&self.connect_db()?)?)
    }

    pub fn add_problem(&self, name: &str, path: &str) {
        let problem = ContestProblemInput {
            name: name.to_owned(),
            path: path.to_owned(),
        };
        let conn = self.connect_db().expect("cannot connect to database");
        diesel::insert_into(schema::problems::table)
            .values(problem)
            .execute(&conn)
            .expect("error executing problem insert query");
    }

    pub fn delete_problem(&self, name: &str) {
        use schema::problems::dsl;
        let conn = self.connect_db().expect("cannot connect to database");
        diesel::delete(dsl::problems.filter(dsl::name.eq(name)))
            .execute(&conn)
            .expect("error executing problem delete query");
    }

    pub fn get_problems(&self) -> Result<Vec<ContestProblem>> {
        Ok(problems::table.load::<ContestProblem>(&self.connect_db()?)?)
    }
}

#[juniper::object(Context = Context)]
impl Contest {
    fn auth(&self, user: String, password: String) -> FieldResult<UserToken> {
        let user = self.get_user(&user)?;
        Ok(UserToken {
            token: auth::auth(&user, &password)?,
        })
    }

    fn user(&self, context: &Context, id: Option<String>) -> FieldResult<user::User> {
        let id = if let Some(id) = &id {
            id
        } else if let Some(ctx) = &context.jwt_data {
            &ctx.user
        } else {
            return Err(FieldError::from("invalid authorization token"));
        };
        Ok(self.get_user(id)?)
    }

    fn problems(&self, context: &Context) -> FieldResult<Vec<ContestProblem>> {
        Ok(self.get_problems()?)
    }

    fn submit(
        &self,
        ctx: &Context,
        problem: String,
        files: Vec<submission::FileInput>,
    ) -> FieldResult<submission::Submission> {
        if let Some(data) = &ctx.jwt_data {
            Ok(submission::insert(
                &self.connect_db()?,
                &data.user,
                &problem,
                files,
            )?)
        } else {
            Err(FieldError::from("Authentication required"))
        }
    }
}
