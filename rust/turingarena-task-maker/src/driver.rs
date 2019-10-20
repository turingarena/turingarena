extern crate failure;

use std::fs;

use std::sync::mpsc::channel;
use std::thread;
use task_maker_format::ui::UIMessage;
use task_maker_format::{ioi, EvaluationConfig};

use turingarena::evaluation::mem::*;
use turingarena::evaluation::record;
use turingarena::evaluation::Event;
use turingarena::problem::{driver::*, material::*, *};
use turingarena::score::Score;
use turingarena::submission::mem::*;

use crate::run_task;
use failure::Error;

pub struct IoiProblemDriver;

fn load_task(pack: ProblemPack) -> Result<ioi::Task, Error> {
    ioi::Task::new(
        pack.0,
        &EvaluationConfig {
            solution_filter: vec![],
            booklet_solutions: false,
            solution_paths: vec![],
        },
    )
}

impl ProblemDriver for IoiProblemDriver {
    type Error = failure::Error;
    type StatError = Self::Error;

    fn stat(pack: ProblemPack) -> Result<ProblemStat, Self::Error> {
        let task = load_task(pack)?;
        Ok(ProblemStat {
            name: ProblemName(task.name),
        })
    }

    fn gen_material(pack: ProblemPack) -> Result<Material, Self::Error> {
        let task = load_task(pack)?;
        Ok(super::material::gen_material(&task))
    }

    fn evaluate(pack: ProblemPack, submission: Submission) -> Evaluation {
        let (tx, rx) = channel::<Event>();
        thread::spawn(move || {
            let dir = tempdir::TempDir::new("evaluation").unwrap();
            let solution = &submission.field_values[0];
            let path = dir.path().join(&solution.file.name.0);
            fs::write(&path, &solution.file.content);
            let (handler, receiver) = run_task(pack.0, path);
            for message in receiver {
                for event in ui_message_to_events(message) {
                    tx.send(event).unwrap();
                }
            }
        });
        Evaluation(rx)
    }
}

fn ui_message_to_events(ui_message: UIMessage) -> Vec<Event> {
    let mut events = Vec::new();
    println!("{:?}", ui_message);
    match ui_message {
        UIMessage::IOITestcaseScore {
            subtask,
            testcase,
            solution,
            score,
            message,
        } => events.push(Event::Value {
            key: record::Key(format!("subtask.{}.testcase.{}.score", subtask, testcase)),
            value: record::Value::Score(Score(score as f64)),
        }),
        UIMessage::IOISubtaskScore {
            subtask,
            solution,
            score,
        } => events.push(Event::Value {
            key: record::Key(format!("subtask.{}.score", subtask)),
            value: record::Value::Score(Score(score as f64)),
        }),
        _ => (),
    }
    events
}
