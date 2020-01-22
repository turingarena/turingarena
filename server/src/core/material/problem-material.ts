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
        attachments: [ProblemAttachment!]!
        "List of awards of this problem"
        awards: [Award]!
        "List of fields that constitute a submission for this problem"
        submissionFields: [SubmissionField!]!
        "List of types that can be associated to files in a submission for this problem"
        submissionFileTypes: [SubmissionFileType!]!
        """
        List of rules used to help users determine the type of a file submitted for a field.
        The first rule that matches the selected field and filename should be used by clients.
        This list should always include a catch-all rule.
        """
        submissionFileTypeRules: [SubmissionFileTypeRule!]!
    }

    type ProblemAttachment {
        title: Text!
        media: Media!
    }

    type SubmissionField {
        name: String!
        title: Text!
    }

    type SubmissionFileType {
        name: String!
        title: Text!
    }

    type SubmissionFileTypeRule {
        """
        Set of fields matched by this rule.
        If null, matches all fields.
        """
        fields: [SubmissionField!]
        """
        Set of file extensions matched by this rule, including the initial dot.
        If null, matches any extension.
        """
        extensions: [String!]

        "Type tu use as default, if not null."
        defaultType: SubmissionFileType
        "List of recommended types the user can choose from. Should include the default type first, if any."
        recommendedTypes: [SubmissionFileType!]!
        "List of other types the user can choose from."
        otherTypes: [SubmissionFileType!]!
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

const defaultType = { name: 'cpp', title: [{ value: 'C/C++' }] };

export const problemMaterialResolversExtensions: ResolversWithModels<{
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
        submissionFields: () => [{ name: 'solution', title: [{ value: 'Solution' }] }],
        submissionFileTypes: () => [defaultType],
        submissionFileTypeRules: () => [{ defaultType, recommendedTypes: [defaultType], otherTypes: [] }],
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
