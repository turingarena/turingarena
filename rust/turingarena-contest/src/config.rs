use crate::schema::config;
use diesel::prelude::*;

/// The configuration of a contest
#[derive(Queryable)]
pub struct Config {
    /// Primary key of the table. Should be *always* 0!
    pub id: i32,

    /// Title of the contest, shown to the users
    pub contest_title: String,

    /// Starting time of the contest, as RFC3339 date
    pub start_time: String,

    /// End time of the contest, as RFC3339 date
    pub end_time: String,
}

#[juniper::object]
impl Config {
    /// Title of the contest, shown to the users
    fn contest_title(&self) -> &String {
        &self.contest_title
    }

    /// Starting time of the contest, as RFC3339 date
    fn start_time(&self) -> &String {
        &self.start_time
    }

    /// End time of the contest, as RFC3339 date
    fn end_time(&self) -> &String {
        &self.end_time
    }

    /// Current time on the server, as RFC3339 date
    fn server_time(&self) -> String {
        chrono::Local::now().to_rfc3339()
    }
}

/// Get the current configuration 
pub fn current_config(conn: &SqliteConnection) -> QueryResult<Config> {
    config::table.first(conn)
}

#[derive(Insertable)]
#[table_name = "config"]
struct ConfigurationInput<'a> {
    contest_title: &'a str,
    start_time: &'a str,
    end_time: &'a str,
}

/// Create a defualt configuration
pub fn create_config(conn: &SqliteConnection, contest_title: &str) -> QueryResult<()> {
    let now = chrono::Local::now();
    let configuration = ConfigurationInput {
        contest_title,
        start_time: &now.to_rfc3339(),
        end_time: &(now + chrono::Duration::hours(4)).to_rfc3339(),
    };
    diesel::insert_into(config::table)
        .values(configuration)
        .execute(conn)?;
    Ok(())
}
