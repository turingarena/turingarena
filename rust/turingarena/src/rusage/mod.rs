#![doc(include = "README.md")]

/// Wraps a memory usage in Bytes
//#[derive(juniper::GraphQlScalarValue)]
pub struct MemoryUsage(pub usize);

/// Wraps a time usage in seconds
//#[derive(juniper::GrapjQLScalarValue)]
pub struct TimeUsage(pub f64);
