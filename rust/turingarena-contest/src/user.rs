use super::*;

use schema::users;

#[derive(Insertable)]
#[table_name = "users"]
pub struct UserInput {
    pub id: String,
    pub display_name: String,
    pub password_bcrypt: String,
}

#[derive(Queryable)]
pub struct User {
    pub id: String,
    pub display_name: String,
    pub password_bcrypt: String,
}

/// A user
#[juniper::object(Context = Context)]
impl User {
    /// ID of this user. Should never be shown to any (non-admin) user.
    fn id(&self) -> String {
        return self.id.clone();
    }

    /// Name of this user to be shown to them or other users.
    fn display_name(&self) -> String {
        return self.display_name.clone();
    }
}
