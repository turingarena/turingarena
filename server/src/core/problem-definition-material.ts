import { gql } from 'apollo-server-core';
import { ApiCache } from '../main/api-cache';
import { ApiContext } from '../main/api-context';
import { createSimpleLoader } from '../main/base-model';
import { ApiOutputValue } from '../main/graphql-types';
import { unreachable } from '../util/unreachable';
import { Contest, ContestCache } from './contest';
import { File } from './data/file';
import { FulfillmentGradeDomain } from './data/fulfillment';
import { Media } from './data/media';
import { ScoreGradeDomain, ScoreRange } from './data/score';
import { Text } from './data/text';
import { ArchiveFileData } from './files/archive';
import { FileContentData } from './files/file-content';
import { ObjectiveDefinition } from './objective-definition';
import { ProblemDefinition } from './problem-definition';
import { submissionFileTypeRules, submissionFileTypes } from './problem-definition-file-types';
import { getProblemTaskInfo, ProblemTaskInfo } from './problem-definition-task-info';

export const problemMaterialSchema = gql`
    extend type ProblemDefinition {
        "Name of this problem to show to users"
        title: Text!
        "Statement of this problem"
        statement: Media!
        "List of attachments of this problem"
        attachments: [ProblemAttachment!]!
        "List of attributes of this problem"
        attributes: [ProblemAttribute!]!
        "List of objectives of this problem"
        objectives: [ObjectiveDefinition]!
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
`;

type Field = ApiOutputValue<'Field'>;

export interface ProblemAttachment {
    title: Text;
    media: Media;
}

export interface ProblemAttribute {
    title: Text;
    field: Field; // FIXME: should not use generated types here
    icon: string;
}

const memoryUnitBytes = 1024 * 1024;

export class ProblemMaterial {
    constructor(readonly problem: ProblemDefinition, readonly taskInfo: ProblemTaskInfo, readonly ctx: ApiContext) {}

    title = new Text([{ value: this.taskInfo.IOI.title }]);

    async statement() {
        return new Media(
            await Promise.all(
                this.taskInfo.IOI.statements.map(
                    async ({ path, language, content_type: type }) =>
                        new File(
                            path.slice(path.lastIndexOf('/') + 1),
                            language,
                            type,
                            await this.loadContent(this.problem, path),
                            this.ctx,
                        ),
                ),
            ),
        );
    }

    async attachments() {
        return Promise.all(
            this.taskInfo.IOI.attachments.map(
                async ({ name, path, content_type: type }): Promise<ProblemAttachment> => ({
                    title: new Text([{ value: name }]),
                    media: new Media([
                        new File(name, null, type, await this.loadContent(this.problem, path), this.ctx),
                    ]),
                }),
            ),
        );
    }

    timeLimitSeconds = this.taskInfo.IOI.limits.time;
    memoryLimitBytes = this.taskInfo.IOI.limits.memory * memoryUnitBytes;

    attributes: ProblemAttribute[] = [
        {
            title: new Text([{ value: 'Time limit' }]),
            field: {
                __typename: 'TimeUsageField',
                timeUsageMaxRelevant: null,
                timeUsage: { __typename: 'TimeUsage', seconds: this.timeLimitSeconds },
                timeUsageWatermark: null,
                valence: null,
            },
            icon: 'stopwatch',
        },
        {
            title: new Text([{ value: 'Memory limit' }]),
            field: {
                __typename: 'MemoryUsageField',
                memoryUsageMaxRelevant: null,
                memoryUsage: { __typename: 'MemoryUsage', bytes: this.memoryLimitBytes },
                memoryUsageWatermark: null,
                valence: null,
            },
            icon: 'microchip',
        },
    ];

    objectives = this.taskInfo.IOI.scoring.subtasks.map(
        (subtask, index): ObjectiveDefinition => new ObjectiveDefinition(this, index),
    );

    submissionFields = [{ name: 'solution', title: new Text([{ value: 'Solution' }]) }];
    submissionFileTypes = submissionFileTypes;
    submissionFileTypeRules = submissionFileTypeRules;

    scoreRange = ScoreRange.total(
        this.objectives
            .map(a => a.gradeDomain)
            .filter((d): d is ScoreGradeDomain => d instanceof ScoreGradeDomain)
            .map(d => d.scoreRange),
    );

    submissionListColumns: Array<ApiOutputValue<'Column'>> = [
        ...this.objectives.map(({ title, gradeDomain }) => {
            if (gradeDomain instanceof ScoreGradeDomain) {
                return { __typename: 'ScoreColumn' as const, title };
            }
            if (gradeDomain instanceof FulfillmentGradeDomain) {
                return { __typename: 'FulfillmentColumn' as const, title };
            }
            throw new Error(`unexpected grade domain ${gradeDomain}`);
        }),
        { __typename: 'ScoreColumn' as const, title: new Text([{ value: 'Total score' }]) },
    ];

    evaluationFeedbackColumns: Array<ApiOutputValue<'Column'>> = [
        { __typename: 'HeaderColumn', title: new Text([{ value: 'Subtask' }]) },
        { __typename: 'HeaderColumn', title: new Text([{ value: 'Case' }]) },
        { __typename: 'TimeUsageColumn', title: new Text([{ value: 'Time usage' }]) },
        { __typename: 'MemoryUsageColumn', title: new Text([{ value: 'Memory usage' }]) },
        { __typename: 'MessageColumn', title: new Text([{ value: 'Message' }]) },
        { __typename: 'ScoreColumn', title: new Text([{ value: 'Score' }]) },
    ];

    async loadContent(problem: ProblemDefinition, path: string) {
        const contest = new Contest(problem.contest.id, this.ctx);
        const { archiveId } = await this.ctx.cache(ContestCache).byId.load(contest.id);
        const file = await this.ctx.table(ArchiveFileData).findOne({
            where: { uuid: archiveId, path: `${problem.baseName}/${path}` },
            include: [this.ctx.table(FileContentData)],
        });

        if (file === null) {
            throw unreachable(`file ${path} not found in problem ${problem.baseName} (referred from metadata)`);
        }

        return file.content();
    }
}

export class ProblemMaterialCache extends ApiCache {
    byId = createSimpleLoader(
        async (id: string) =>
            new ProblemMaterial(
                ProblemDefinition.fromId(id, this.ctx),
                await getProblemTaskInfo(this.ctx, ProblemDefinition.fromId(id, this.ctx)),
                this.ctx,
            ),
    );
}
