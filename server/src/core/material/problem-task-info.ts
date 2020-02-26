import * as fs from 'fs';
import { DateTime } from 'luxon';
import * as path from 'path';
import { FileContent } from '../file-content';
import { Problem } from '../problem';
import { ProblemFile } from '../problem-file';

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

export async function getProblemTaskInfo(problem: Problem): Promise<ProblemTaskInfo> {
    const root = problem.root;
    const metadataPath = '.task-info.json';
    const metadataProblemFile = await root.table(ProblemFile).findOne({
        where: {
            // FIXME: fix typing of .id in some BaseModel
            problemId: problem.id as string,
            path: metadataPath,
        },
        include: [root.table(FileContent).scope('withData')],
    });

    if (metadataProblemFile === null) {
        throw new Error(`Problem ${problem.name} is missing metadata file ${metadataPath}`);
    }

    return JSON.parse(metadataProblemFile.content.content.toString()) as ProblemTaskInfo;
}

/**
 * Extract the files of this problem in the specified base dir:
 * ${base}/${this.name}/${this.updatedAt}/<files...>
 * The last updated timestamp of this problem is appended, and
 * nothing is done if the directory already exists.
 * Creates all the directories if they don't exist.
 *
 * @param base Base directory
 */
export async function extractProblemFiles(problem: Problem, base: string) {
    const problemDir = path.join(
        base,
        problem.name,
        // FIXME: make updatedAt be correctly typed in some BaseModel
        DateTime.fromJSDate(problem.updatedAt as Date).toFormat('x--yyyy-MM-dd--hh-mm-ss'),
    );

    try {
        if ((await fs.promises.stat(problemDir)).isDirectory()) return problemDir;
    } catch {
        // Directory doesn't exist and thus stat fails
    }

    const problemFiles = await problem.getFiles({
        include: [problem.root.table(FileContent).scope('withData')],
    });

    for (const problemFile of problemFiles) {
        const filePath = path.join(problemDir, problemFile.path);
        await problemFile.content.extract(filePath);
    }

    return problemDir;
}

/**
 * Import the problem files from the filesystem
 *
 * @param root Model root to use
 * @param base Base directory to add
 * @param dir  Current directory
 */
export async function importProblemFiles(problem: Problem, base: string, dir: string = '') {
    const root = problem.root;
    const files = fs.readdirSync(path.join(base, dir));
    for (const file of files) {
        const relPath = path.join(dir, file);
        if (fs.statSync(path.join(base, relPath)).isDirectory()) {
            await importProblemFiles(problem, base, relPath);
        } else {
            const content = await FileContent.createFromPath(root, path.join(base, relPath));
            await problem.createFile({
                path: relPath,
                contentId: content.id,
            });
        }
    }
}
