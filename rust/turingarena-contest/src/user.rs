use super::*;

use schema::users;

#[derive(Insertable, juniper::GraphQLInputObject)]
#[table_name = "users"]
pub struct UserInput {
    pub id: String,
    pub display_name: String,
    pub password: String,
}

#[derive(Queryable)]
pub struct User {
    pub id: String,
    pub display_name: String,
    pub password: String,
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

    /// checks the user password
    fn check_password(&self, password: String) -> bool {
        bcrypt::verify(&password, &self.password).unwrap()
    }
}

pub struct UserRepository;

impl UserRepository {
}
