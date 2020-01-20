import * as fs from 'fs';
import { DateTime } from 'luxon';
import * as path from 'path';
import { ApiContext } from '../main/context';
import { FileContent } from './file-content';
import { Problem } from './problem';
import { ProblemFile } from './problem-file';

/** Generic problem metadata */
export interface ProblemMetadata {
    version: number;
    task_type: string;
    name: string;
    title: string;
    limits: {
        time: number;
        memory: number;
    };
    scoring: {
        max_score: number;
        subtasks: SubtaskMetadata[];
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

export interface SubtaskMetadata {
    max_score: number;
    testcases: number;
}

export async function getProblemMetadata(ctx: ApiContext, problem: Problem): Promise<ProblemMetadata> {
    const metadataPath = '.task-info.json';
    const metadataProblemFile = await ctx.table(ProblemFile).findOne({
        where: {
            // FIXME: fix typing of .id in some BaseModel
            problemId: problem.id as string,
            path: metadataPath,
        },
        include: [ctx.table(FileContent).scope('withData')],
    });

    if (metadataProblemFile === null) {
        throw new Error(`Problem ${problem.name} is missing metadata file ${metadataPath}`);
    }

    return JSON.parse(metadataProblemFile.content.content.toString()) as ProblemMetadata;
}

/**
 * Extract the files of this problem in the specified base dir:
 * ${base}/${this.name}/${this.updatedAt}/<files...>
 * The last updated timestamp of this problem is appended, and
 * nothing is done if the directory already exists.
 * Creates all the directories if they don't exist.
 *
 * @param ctx Context to use
 * @param base Base directory
 */
export async function extractProblemFiles(ctx: ApiContext, problem: Problem, base: string) {
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
        include: [ctx.table(FileContent).scope('withData')],
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
 * @param ctx  Context to use
 * @param base Base directory to add
 * @param dir  Current directory
 */
export async function importProblemFiles(ctx: ApiContext, problem: Problem, base: string, dir: string = '') {
    const files = fs.readdirSync(path.join(base, dir));
    for (const file of files) {
        const relPath = path.join(dir, file);
        if (fs.statSync(path.join(base, relPath)).isDirectory()) {
            await importProblemFiles(ctx, problem, base, relPath);
        } else {
            const content = await FileContent.createFromPath(ctx, path.join(base, relPath));
            await problem.createFile({
                path: relPath,
                contentId: content.id,
            });
        }
    }
}
