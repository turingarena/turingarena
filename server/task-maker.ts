import {spawn} from "child_process";
import * as which from "which";

interface TaskMetadata {
    version: number,
    task_type: string,
    name: string,
    title: string,
    limits: {
        time: number,
        memory: number,
    }
    scoring: {
        max_score: number,
        subtasks: Array<{
            max_score: number,
            testcases: number,
        }>,
    },
    statements: Array<{
        language: string,
        content_type: string,
        path: string,
    }>,
    attachments: Array<{
        name: string,
        content_type: string,
        path: string,
    }>
}

/**
 * Searches for the task-maker executable in the following locations:
 * - TASK_MAKER_EXE variable
 * - task-maker-rust in PATH
 * - task-maker in PATH
 *
 * @return the task maker path
 */
async function findTaskMakerExecutable(): Promise<string> {
    const exe = process.env.TASK_MAKER_EXE;
    if (exe != undefined)
        return exe;
    try {
        return await which("task-maker-rust");
    } catch {
        return which("task-maker");
    }
}

/**
 * Generates the metadata of a task-maker task
 *
 * @param path location of the task
 * @return the task metadata
 */
export async function taskMetadata(path: string): Promise<TaskMetadata> {
    const args = [
        "--ui=json",
        "--task-info",
        "--task-dir",
        path
    ];
    let metadata = "";
    let process = spawn(await findTaskMakerExecutable(), args);
    process.stdout.on("data", data => metadata += data);
    return new Promise<TaskMetadata>((resolve, reject) => {
        process.on("close", code => {
            console.log(metadata);
            if (code != 0)
                reject(`task-maker error: return code ${code} != 0`);
            else
                resolve(JSON.parse(metadata))
        })
    })
}

taskMetadata("/home/ale/git/oii/oii/problemi/taglialegna").then(console.log);