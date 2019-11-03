#![doc(include = "README.md")]

use serde::{Deserialize, Serialize};

/// Wraps a memory usage in Bytes
#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct MemoryUsage(pub i32);

juniper::graphql_object!(MemoryUsage: () where Scalar = <S> |&self| {
    field bytes() -> i32 {
        self.0
    }
});

/// Wraps a time usage in seconds
#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct TimeUsage(pub f64);

juniper::graphql_object!(TimeUsage: () where Scalar = <S> |&self| {
    field seconds() -> f64 {
        self.0
    }
});
