import { ApiContext } from '../../main/context';
import { FileContent } from '../file-content';
import { Problem } from '../problem';
import { ProblemFile } from '../problem-file';
import { getProblemMetadata } from '../problem-util';
import { MediaVariant } from './media';
import { ProblemAttachment, ProblemMaterial } from './problem-material';

async function loadContent(ctx: ApiContext, problem: Problem, path: string) {
    return (
        (await ctx.table(ProblemFile).findOne({
            where: {
                problemId: problem.id as string,
                path,
            },
            include: [ctx.table(FileContent)],
        })) ?? ctx.fail(`file ${path} not found in problem ${problem.name} (referred from metadata)`)
    ).content;
}

export async function getProblemMaterial(ctx: ApiContext, problem: Problem): Promise<ProblemMaterial> {
    const { title, attachments, statements } = await getProblemMetadata(ctx, problem);

    return {
        title: [
            {
                value: title,
            },
        ],
        statement: await Promise.all(
            statements.map(
                async ({ path, language, content_type: type }): Promise<MediaVariant> => ({
                    name: path.slice(path.lastIndexOf('/') + 1),
                    language,
                    type,
                    content: await loadContent(ctx, problem, path),
                }),
            ),
        ),
        attachments: await Promise.all(
            attachments.map(
                async ({ name, path, content_type: type }): Promise<ProblemAttachment> => ({
                    title: [{ value: name }],
                    media: [
                        {
                            name,
                            type,
                            content: await loadContent(ctx, problem, path),
                        },
                    ],
                }),
            ),
        ),
    };
}
