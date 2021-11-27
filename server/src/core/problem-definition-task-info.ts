import { ApiContext } from '../main/api-context';
import { unreachable } from '../util/unreachable';
import { ProblemDefinition } from './problem-definition';

export interface ProblemTaskInfo {
    IOI: IOITaskInfo;
    Terry: object; // TODO
}

export interface IOITaskInfo {
    version: number;
    name: string;
    title: string;
    limits: {
        time: number;
        memory: number;
    };
    scoring: {
        max_score: number;
        subtasks: Array<{
            max_score: number;
            testcases: number;
        }>;
    };
    statements: Array<{
        language: string;
        content_type: string;
        path: string;
    }>;
    attachments: Array<{
        name: string;
        content_type: string;
        path: string;
    }>;
}

export async function getProblemTaskInfo(ctx: ApiContext, problem: ProblemDefinition): Promise<ProblemTaskInfo> {
    const problemPackage = await problem.packageUnchecked();
    const revision = await problemPackage.mainRevision();
    const archive = revision?.archive() ?? null;

    if (archive === null) throw unreachable(`problem has no archive`);

    const taskInfoJson = await archive.fileContent(`.task-info.json`);
    if (taskInfoJson === null) throw unreachable(`problem is missing task-info file`); // FIXME

    return JSON.parse(taskInfoJson.utf8()) as ProblemTaskInfo;
}
