import { ApiContext } from '../../main/api-context';
import { ContestCache } from '../contest';
import { ArchiveFileData } from '../files/archive';
import { FileContent } from '../files/file-content';
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

export async function getProblemTaskInfo(ctx: ApiContext, problem: Problem): Promise<ProblemTaskInfo> {
    const { archiveId } = await ctx.cache(ContestCache).byId.load(problem.contest.id);
    const metadataPath = `${problem.name}/.task-info.json`;

    const metadataProblemFile = await ctx.table(ArchiveFileData).findOne({
        where: { uuid: archiveId, path: metadataPath },
    });

    if (metadataProblemFile === null) {
        throw new Error(`Problem ${problem.name} is missing metadata file ${metadataPath}`);
    }

    const metadataContent = await ctx.table(FileContent).findOne({ where: { id: metadataProblemFile.contentId } });

    return JSON.parse(metadataContent!.content.toString()) as ProblemTaskInfo;
}
