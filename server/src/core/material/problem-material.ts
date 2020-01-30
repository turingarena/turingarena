import { gql } from 'apollo-server-core';
import { Resolvers } from '../../main/resolver-types';
import { FulfillmentGradeDomain } from '../feedback/fulfillment';
import { ScoreGradeDomain, ScoreRange } from '../feedback/score';
import { FileContent } from '../file-content';
import { Problem } from '../problem';
import { ProblemFile } from '../problem-file';
import { Award } from './award';
import { Media, MediaVariant } from './media';
import { ProblemTaskInfo } from './problem-task-info';
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

        "Columns of the table of submissions for this problem."
        submissionListColumns: [Column!]!

        "Columns of the table containing evaluation feedback for submissions for this problem."
        evaluationFeedbackColumns: [Column!]!

        totalScoreDomain: ScoreGradeDomain!
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

export class ProblemMaterial {
    constructor(readonly problem: Problem, readonly taskInfo: ProblemTaskInfo) {}

    title = [{ value: this.taskInfo.title }];
    statement = this.taskInfo.statements.map(
        ({ path, language, content_type: type }): MediaVariant => ({
            name: path.slice(path.lastIndexOf('/') + 1),
            language,
            type,
            content: () => loadContent(this.problem, path),
        }),
    );

    attachments = this.taskInfo.attachments.map(
        ({ name, path, content_type: type }): ProblemAttachment => ({
            title: [{ value: name }],
            media: [
                {
                    name,
                    type,
                    content: () => loadContent(this.problem, path),
                },
            ],
        }),
    );

    awards = this.taskInfo.scoring.subtasks.map((subtask, index): Award => new Award(this, index));

    submissionFields = [{ name: 'solution', title: [{ value: 'Solution' }] }];
    submissionFileTypes = [defaultType];
    submissionFileTypeRules = [{ defaultType, recommendedTypes: [defaultType], otherTypes: [] }];

    scoreRange = ScoreRange.total(
        this.awards
            .map(a => a.gradeDomain)
            .filter((d): d is ScoreGradeDomain => d instanceof ScoreGradeDomain)
            .map(d => d.scoreRange),
    );

    submissionListColumns = [
        ...this.awards.map(({ title, gradeDomain }) => {
            if (gradeDomain instanceof ScoreGradeDomain) return { __typename: 'ScoreColumn', title };
            if (gradeDomain instanceof FulfillmentGradeDomain) return { __typename: 'FulfillmentColumn', title };
            throw new Error(`unexpected grade domain ${gradeDomain}`);
        }),
        {
            __typename: 'ScoreColumn',
            title: [{ value: 'Total score' }],
        },
    ];

    evaluationFeedbackColumns = [
        {
            __typename: 'IndexHeaderColumn',
            title: [{ value: 'Subtask' }],
        },
        {
            __typename: 'IndexHeaderColumn',
            title: [{ value: 'Case' }],
        },
        {
            __typename: 'TimeUsageColumn',
            title: [{ value: 'Time usage' }],
        },
        {
            __typename: 'MemoryUsageColumn',
            title: [{ value: 'Memory usage' }],
        },
        {
            __typename: 'MessageColumn',
            title: [{ value: 'Message' }],
        },
        {
            __typename: 'ScoreColumn',
            title: [{ value: 'Score' }],
        },
    ];
}

const defaultType = { name: 'cpp', title: [{ value: 'C/C++' }] };

export interface ProblemMaterialModelRecord {
    ProblemAttachment: ProblemAttachment;
}

export const problemMaterialResolversExtensions: Resolvers = {
    Problem: {
        title: async problem => (await problem.getMaterial()).title,
        statement: async problem => (await problem.getMaterial()).statement,
        attachments: async problem => (await problem.getMaterial()).attachments,
        awards: async problem => (await problem.getMaterial()).awards,
        submissionFields: async problem => (await problem.getMaterial()).submissionFields,
        submissionFileTypes: async problem => (await problem.getMaterial()).submissionFileTypes,
        submissionFileTypeRules: async problem => (await problem.getMaterial()).submissionFileTypeRules,
        submissionListColumns: async problem => (await problem.getMaterial()).submissionListColumns,
        evaluationFeedbackColumns: async problem => (await problem.getMaterial()).evaluationFeedbackColumns,
    },
};

async function loadContent(problem: Problem, path: string) {
    const root = problem.root;

    return (
        (await root.table(ProblemFile).findOne({
            where: {
                problemId: problem.id as string,
                path,
            },
            include: [root.table(FileContent)],
        })) ?? root.fail(`file ${path} not found in problem ${problem.name} (referred from metadata)`)
    ).content;
}
