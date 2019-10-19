use juniper::{FieldError, FieldResult};

use crate::*;
use schema::{problems, users};

#[derive(Clone)]
pub struct Contest {
    database_url: String,
}

/// a user authorization token
#[derive(juniper::GraphQLObject)]
pub struct UserToken {
    token: Option<String>,
}

impl Contest {
    pub fn from_env() -> Contest {
        let database_url = std::env::var("DATABASE_URL").unwrap_or("./database.sqlite3".to_owned());
        Contest::with_database(database_url)
    }

    pub fn with_database(database_url: String) -> Contest {
        Contest { database_url }
    }

    pub fn connect_db(&self) -> ConnectionResult<SqliteConnection> {
        SqliteConnection::establish(&self.database_url)
    }

    pub fn init_db(&self) {
        let connection = self.connect_db().expect("Error connecting to the database");
        embedded_migrations::run_with_output(&connection, &mut std::io::stdout())
            .expect("Error while initializing the database");
    }

    pub fn add_user(&self, id: String, display_name: String, password: String) {
        use crate::user::UserInput;
        let user = UserInput {
            id,
            display_name,
            password: bcrypt::hash(password, bcrypt::DEFAULT_COST).unwrap(),
        };
        let conn = self.connect_db().expect("cannot connect to database");
        diesel::insert_into(schema::users::table)
            .values(user)
            .execute(&conn)
            .expect("error executing user insert query");
    }

    pub fn delete_user(&self, id: String) {
        use schema::users::dsl;
        let conn = self.connect_db().expect("cannot connect to database");
        diesel::delete(dsl::users.filter(dsl::id.eq(id)))
            .execute(&conn)
            .expect("error executing user delete query");
    }

    pub fn add_problem(&self, name: String) {
        use crate::problem::ProblemInput;
        let problem = ProblemInput { name };
        let conn = self.connect_db().expect("cannot connect to database");
        diesel::insert_into(schema::problems::table)
            .values(problem)
            .execute(&conn)
            .expect("error executing problem insert query");
    }

    pub fn delete_problem(&self, name: String) {
        use schema::problems::dsl;
        let conn = self.connect_db().expect("cannot connect to database");
        diesel::delete(dsl::problems.filter(dsl::name.eq(name)))
            .execute(&conn)
            .expect("error executing problem delete query");
    }
}

#[juniper::object(Context = Context)]
impl Contest {
    fn auth(&self, user: String, password: String) -> FieldResult<UserToken> {
        let connection = self.connect_db()?;
        let user = users::table.find(user).first(&connection)?;
        Ok(UserToken {
            token: auth::auth(&user, &password),
        })
    }

    fn user(&self, context: &Context, id: Option<String>) -> FieldResult<user::User> {
        let connection = self.connect_db()?;
        let id = if let Some(id) = &id {
            id
        } else if let Some(ctx) = &context.jwt_data {
            &ctx.user
        } else {
            return Err(FieldError::from("invalid authorization token"));
        };
        Ok(users::table.find(id).first(&connection)?)
    }

    fn problems(&self, context: &Context) -> FieldResult<Vec<problem::Problem>> {
        let connection = self.connect_db()?;
        return Ok(problems::table.load::<problem::Problem>(&connection)?);
    }
}
