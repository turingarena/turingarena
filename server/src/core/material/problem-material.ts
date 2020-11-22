import { gql } from 'apollo-server-core';
import { __generated_Field } from '../../generated/graphql-types';
import { ApiObject } from '../../main/api';
import { ApiContext } from '../../main/api-context';
import { createSimpleLoader } from '../../main/base-model';
import { Contest, ContestApi } from '../contest';
import { FulfillmentGradeDomain } from '../feedback/fulfillment';
import { ScoreGradeDomain, ScoreRange } from '../feedback/score';
import { Archive } from '../files/archive';
import { FileContent } from '../files/file-content';
import { Problem } from '../problem';
import { Award } from './award';
import { Media, MediaFile } from './media';
import { ProblemTaskInfo, ProblemTaskInfoApi } from './problem-task-info';
import { Text } from './text';

export const problemMaterialSchema = gql`
    extend type Problem {
        "Name of this problem to show to users"
        title: Text!
        "Statement of this problem"
        statement: Media!
        "List of attachments of this problem"
        attachments: [ProblemAttachment!]!
        "List of attributes of this problem"
        attributes: [ProblemAttribute!]!
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

    """
    Attributes of a problem identified by a title and containing a field
    """
    type ProblemAttribute {
        title: Text!
        field: Field!
        icon: String
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

export interface ProblemAttribute {
    title: Text;
    field: __generated_Field; // FIXME: should not use generated types here
    icon: string;
}

const languages = {
    python2: {
        name: 'python2',
        title: [{ value: 'Python 2 (cpython)' }],
    },
    python3: {
        name: 'py',
        title: [{ value: 'Python 3 (cpython)' }],
    },
    c: {
        name: 'c',
        title: [{ value: 'C (c11)' }],
    },
    cpp: {
        name: 'cpp',
        title: [{ value: 'C++ (c++17)' }],
    },
    rust: {
        name: 'rust',
        title: [{ value: 'Rust' }],
    },
    java: {
        name: 'java',
        title: [{ value: 'Java 8 (JDK)' }],
    },
};

const fileRules = [
    {
        extensions: ['.c', '.h'],
        defaultType: languages.c,
        recommendedTypes: [languages.c],
        otherTypes: [languages.cpp],
    },
    {
        extensions: ['.py'],
        defaultType: languages.python3,
        recommendedTypes: [languages.python3, languages.python2],
        otherTypes: [],
    },
    {
        extensions: ['.cpp', '.hpp', '.cc', '.cxx'],
        defaultType: languages.cpp,
        recommendedTypes: [languages.cpp],
        otherTypes: [],
    },
    {
        extensions: ['.java'],
        defaultType: languages.java,
        recommendedTypes: [languages.java],
        otherTypes: [],
    },
    {
        extensions: ['.rs'],
        defaultType: languages.rust,
        recommendedTypes: [languages.rust],
        otherTypes: [],
    },
];

const memoryUnitBytes = 1024 * 1024;

export class ProblemMaterial {
    constructor(readonly problem: Problem, readonly taskInfo: ProblemTaskInfo) {}

    title = [{ value: this.taskInfo.IOI.title }];
    statement = this.taskInfo.IOI.statements.map(
        ({ path, language, content_type: type }): MediaFile =>
            new MediaFile(path.slice(path.lastIndexOf('/') + 1), language, type, ctx =>
                this.loadContent(ctx, this.problem, path),
            ),
    );

    attachments = this.taskInfo.IOI.attachments.map(
        ({ name, path, content_type: type }): ProblemAttachment => ({
            title: [{ value: name }],
            media: [new MediaFile(name, null, type, ctx => this.loadContent(ctx, this.problem, path))],
        }),
    );

    timeLimitSeconds = this.taskInfo.IOI.limits.time;
    memoryLimitBytes = this.taskInfo.IOI.limits.memory * memoryUnitBytes;

    attributes: ProblemAttribute[] = [
        {
            title: [{ value: 'Time limit' }],
            field: {
                __typename: 'TimeUsageField',
                timeUsageMaxRelevant: {
                    __typename: 'TimeUsage',
                    seconds: this.timeLimitSeconds,
                },
                timeUsage: {
                    __typename: 'TimeUsage',
                    seconds: this.timeLimitSeconds,
                },
            },
            icon: 'stopwatch',
        },
        {
            title: [{ value: 'Memory limit' }],
            field: {
                __typename: 'MemoryUsageField',
                memoryUsageMaxRelevant: {
                    __typename: 'MemoryUsage',
                    bytes: this.memoryLimitBytes,
                },
                memoryUsage: {
                    __typename: 'MemoryUsage',
                    bytes: this.memoryLimitBytes,
                },
            },
            icon: 'microchip',
        },
    ];

    awards = this.taskInfo.IOI.scoring.subtasks.map((subtask, index): Award => new Award(this, index));

    submissionFields = [{ name: 'solution', title: [{ value: 'Solution' }] }];
    submissionFileTypes = Object.values(languages);
    submissionFileTypeRules = fileRules;

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
            __typename: 'HeaderColumn',
            title: [{ value: 'Subtask' }],
        },
        {
            __typename: 'HeaderColumn',
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

    async loadContent(ctx: ApiContext, problem: Problem, path: string) {
        const contest = new Contest(problem.contest.id, ctx);
        const { archiveId } = await ctx.api(ContestApi).dataLoader.load(contest.id);
        const file = await ctx.table(Archive).findOne({
            where: { uuid: archiveId, path: `${problem.name}/${path}` },
            include: [ctx.table(FileContent)],
        });

        if (file === null) {
            throw ctx.fail(`file ${path} not found in problem ${problem.name} (referred from metadata)`);
        }

        return file.content;
    }
}

export interface ProblemMaterialModelRecord {
    ProblemAttachment: ProblemAttachment;
}

export class ProblemMaterialApi extends ApiObject {
    dataLoader = createSimpleLoader(
        async (id: string) =>
            new ProblemMaterial(
                Problem.fromId(id, this.ctx),
                await this.ctx.api(ProblemTaskInfoApi).getProblemTaskInfo(Problem.fromId(id, this.ctx)),
            ),
    );
}
