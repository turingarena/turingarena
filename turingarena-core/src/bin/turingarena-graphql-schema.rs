use turingarena::*;

use contest::graphql_schema::generate_schema;

fn main() {
    println!("{}", generate_schema());
}
