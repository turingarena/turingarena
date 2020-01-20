import { gql } from 'apollo-server-core';
import { ResolverFn } from '../../generated/graphql-types';
import { ApiContext } from '../../main/context';
import { ResolversWithModels } from '../../main/resolver-types';
import { Award } from '../award';
import { FileContent } from '../file-content';
import { Problem } from '../problem';
import { ProblemFile } from '../problem-file';
import { getProblemMetadata, ProblemMetadata } from '../problem-util';
import { Media, MediaVariant } from './media';
import { Text } from './text';

export const problemMaterialSchema = gql`
    extend type Problem {
        "Name of this problem to show to users"
        title: Text!
        "Statement of this problem"
        statement: Media!
        "List of attachments of this problem"
        attachments: [ProblemAttachment]!
        "List of awards of this problem"
        awards: [Award]!
    }

    type ProblemAttachment {
        title: Text!
        media: Media!
    }
`;

export interface ProblemAttachment {
    title: Text;
    media: Media;
}

/** Transforms a resolver by loading problem metadata first */
function withProblemMetadata<TResult, TArgs>(
    resolver: ResolverFn<TResult, { metadata: ProblemMetadata; problem: Problem }, ApiContext, TArgs>,
): ResolverFn<TResult, Problem, ApiContext, TArgs> {
    return async (problem, args, ctx, info) =>
        resolver({ metadata: await getProblemMetadata(ctx, problem), problem }, args, ctx, info);
}

export const problemMaterialResolvers: ResolversWithModels<{
    Problem: Problem;
}> = {
    Problem: {
        title: withProblemMetadata(({ metadata: { title } }) => [{ value: title }]),
        statement: withProblemMetadata(({ problem, metadata: { statements } }, {}, ctx) =>
            statements.map(
                async ({ path, language, content_type: type }): Promise<MediaVariant> => ({
                    name: path.slice(path.lastIndexOf('/') + 1),
                    language,
                    type,
                    content: await loadContent(ctx, problem, path),
                }),
            ),
        ),
        attachments: withProblemMetadata(({ problem, metadata: { attachments } }, {}, ctx) =>
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
        awards: withProblemMetadata(({ problem, metadata: { scoring: { subtasks } } }) =>
            subtasks.map((subtask, index): Award => ({ problem, index })),
        ),
    },
};

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
