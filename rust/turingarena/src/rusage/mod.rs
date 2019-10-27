#![doc(include = "README.md")]

use serde::{Deserialize, Serialize};

/// Wraps a memory usage in Bytes
#[derive(Serialize, Deserialize, Clone, Debug, juniper::GraphQLScalarValue)]
pub struct MemoryUsage(pub i32);

/// Wraps a time usage in seconds
#[derive(Serialize, Deserialize, Clone, Debug, juniper::GraphQLScalarValue)]
pub struct TimeUsage(pub f64);
