pub struct ImportMutation;

pub mod import_mutation {
    #![allow(dead_code)]

    pub const OPERATION_NAME: &'static str = "ImportMutation";
    pub const QUERY: &'static str = "mutation ImportMutation($input: ImportInput!) {\n    import(input: $input) {\n        ok\n    }\n}\n";

    use serde::{Serialize, Deserialize};

    #[allow(dead_code)]
    type Boolean = bool;
    #[allow(dead_code)]
    type Float = f64;
    #[allow(dead_code)]
    type Int = i64;
    #[allow(dead_code)]
    type ID = String;

    #[derive(Serialize)]
    pub struct ImportInput { #[serde(rename = "contentBase64")] pub content_base64: String, pub name: Option<String>, pub type : Option < String >, }

#[derive(Deserialize)]
pub struct ImportMutationImport { pub ok: Boolean }

#[derive(Serialize)]
pub struct Variables { pub input: ImportInput }

impl Variables {}

#[derive(Deserialize)]
pub struct ResponseData { #[doc = "Import a file"] pub import: ImportMutationImport } } impl graphql_client::GraphQLQuery for ImportMutation { type Variables = import_mutation::Variables; type ResponseData = import_mutation::ResponseData; fn build_query ( variables: Self ::Variables ) ->::graphql_client::QueryBody < Self ::Variables > { graphql_client::QueryBody { variables, query: import_mutation::QUERY, operation_name: import_mutation::OPERATION_NAME, } } }