///! Contains a trait to implement to support a problem format.
use std::path;

use super::*;
use crate::*;

pub struct ProblemStat {
    pub name: ProblemName,
}

pub struct ProblemPack(pub path::PathBuf);

pub trait ProblemDriver {
    type StatError;
    type Error;

    fn stat(pack: ProblemPack) -> Result<ProblemStat, Self::StatError>;
    fn gen_material(pack: ProblemPack) -> Result<material::Material, Self::Error>;
    fn evaluate(
        pack: ProblemPack,
        submission: submission::mem::Submission,
    ) -> evaluation::mem::Evaluation;
}
