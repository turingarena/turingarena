extern crate serde;

use super::content::*;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Clone)]
pub struct FieldId(pub String);

#[derive(Serialize, Deserialize, Clone)]
pub struct Field {
    pub id: FieldId,
    pub title: Text,
    pub types: Vec<FileType>,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct FileTypeId(pub String);

#[derive(Serialize, Deserialize, Clone)]
pub struct FileTypeExtension(pub String);

#[derive(Serialize, Deserialize, Clone)]
pub struct FileType {
    pub id: FileTypeId,
    pub title: Text,
    pub extensions: Vec<FileTypeExtension>,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct Form {
    pub fields: Vec<Field>,
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
