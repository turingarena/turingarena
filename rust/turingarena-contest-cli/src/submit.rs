use crate::client;
use graphql_client::{GraphQLQuery, Response};
use std::fs;
use std::path::PathBuf;

#[derive(GraphQLQuery)]
#[graphql(
    schema_path = "graphql/schema.json",
    query_path = "graphql/submit.graphql",
    result_derive = "Debug"
)]
struct SubmitMutation;

fn parse_files(files: Vec<String>) -> Vec<submit_mutation::FileInput> {
    let mut result = Vec::new();
    for file in files {
        let parts: Vec<&str> = file.split("=").collect();
        if parts.len() > 2 {
            panic!("Error parsing file string, too many =");
        }
        let (field, path) = if parts.len() == 2 {
            (parts[0], parts[1])
        } else {
            ("solution", parts[0])
        };
        let path = PathBuf::from(path);
        if !path.exists() {
            panic!("Input file {:?} doesn't exist", &path);
        }
        let content = fs::read(&path).expect(&format!("Error reading file {:?}", &path));
        let content_base64 = base64::encode(&content);
        result.push(submit_mutation::FileInput {
            type_id: "text/plain".to_owned(), // TODO: get file type
            field_id: field.to_owned(),
            name: path.file_name().unwrap().to_str().unwrap().to_owned(),
            content_base64,
        });
    }
    result
}

/// send a submission to the TuringArena server
pub fn submit(problem: String, files: Vec<String>) {
    let variables = submit_mutation::Variables {
        problem,
        files: parse_files(files),
    };

    let query_body = SubmitMutation::build_query(variables);
    let response: Response<submit_mutation::ResponseData> =
        client::authenticated_request(&query_body);

    if let Some(errors) = response.errors {
        for error in errors {
            eprintln!("Error submitting: {}", error.message);
        }
        panic!("Error submitting query");
    }

    if let Some(data) = response.data {
        println!(
            "Submission registered with id = {} at time {}",
            data.submit.id, data.submit.created_at
        )
    }
}
