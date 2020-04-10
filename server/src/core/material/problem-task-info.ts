import { FileCollection } from '../file-collection';
import { FileContent } from '../file-content';
import { Problem } from '../problem';

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
    const metadataProblemFile = await root.table(FileCollection).findOne({
        where: {
            uuid: problem.fileCollectionId,
            path: metadataPath,
        },
    });

    if (metadataProblemFile === null) {
        throw new Error(`Problem ${problem.name} is missing metadata file ${metadataPath}`);
    }

    const metadataContent = await root.table(FileContent).findOne({ where: { id: metadataProblemFile.contentId } });

    return JSON.parse(metadataContent!.content.toString()) as ProblemTaskInfo;
}
