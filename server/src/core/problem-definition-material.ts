import { gql } from 'apollo-server-core';
import { ApiCache } from '../main/api-cache';
import { ApiContext } from '../main/api-context';
import { createSimpleLoader } from '../main/base-model';
import { ApiOutputValue } from '../main/graphql-types';
import { unreachable } from '../util/unreachable';
import { Field } from './data/field';
import { File } from './data/file';
import { FulfillmentColumn, FulfillmentGradeDomain } from './data/fulfillment';
import { HeaderColumn } from './data/header';
import { Media } from './data/media';
import { MemoryUsage, MemoryUsageColumn, MemoryUsageField } from './data/memory-usage';
import { MessageColumn } from './data/message';
import { ScoreColumn, ScoreGradeDomain, ScoreRange } from './data/score';
import { Text } from './data/text';
import { TimeUsage, TimeUsageColumn, TimeUsageField } from './data/time-usage';
import { FileContentService } from './files/file-content-service';
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

export interface ProblemAttachment {
    title: Text;
    media: Media;
}

export class ProblemAttribute implements ApiOutputValue<'ProblemAttribute'> {
    constructor(readonly title: Text, readonly field: Field, readonly icon: string) {}

    __typename = 'ProblemAttribute' as const;
}

export class SubmissionField implements ApiOutputValue<'SubmissionField'> {
    constructor(readonly name: string, readonly title: Text) {}

    __typename = 'SubmissionField' as const;
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
                            await this.loadPublicContent(this.problem, path),
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
                        new File(name, null, type, await this.loadPublicContent(this.problem, path), this.ctx),
                    ]),
                }),
            ),
        );
    }

    timeLimitSeconds = this.taskInfo.IOI.limits.time;
    memoryLimitBytes = this.taskInfo.IOI.limits.memory * memoryUnitBytes;

    attributes = [
        new ProblemAttribute(
            new Text([{ value: 'Time limit' }]),
            new TimeUsageField(new TimeUsage(this.timeLimitSeconds), null, null, null),
            'stopwatch',
        ),
        new ProblemAttribute(
            new Text([{ value: 'Memory limit' }]),
            new MemoryUsageField(new MemoryUsage(this.memoryLimitBytes), null, null, null),
            'microchip',
        ),
    ];

    objectives = this.taskInfo.IOI.scoring.subtasks.map(
        (subtask, index): ObjectiveDefinition => new ObjectiveDefinition(this, index),
    );

    submissionFields = [new SubmissionField('solution', new Text([{ value: 'Solution' }]))];
    submissionFileTypes = submissionFileTypes;
    submissionFileTypeRules = submissionFileTypeRules;

    scoreRange = ScoreRange.total(
        this.objectives
            .map(a => a.gradeDomain)
            .filter((d): d is ScoreGradeDomain => d instanceof ScoreGradeDomain)
            .map(d => d.scoreRange),
    );

    submissionListColumns = [
        ...this.objectives.map(({ title, gradeDomain }) => {
            if (gradeDomain instanceof ScoreGradeDomain) return new ScoreColumn(title);
            if (gradeDomain instanceof FulfillmentGradeDomain) return new FulfillmentColumn(title);
            throw new Error(`unexpected grade domain ${gradeDomain}`);
        }),
        new ScoreColumn(new Text([{ value: 'Total score' }])),
    ];

    evaluationFeedbackColumns = [
        new HeaderColumn(new Text([{ value: 'Subtask' }])),
        new HeaderColumn(new Text([{ value: 'Case' }])),
        new TimeUsageColumn(new Text([{ value: 'Time usage' }])),
        new MemoryUsageColumn(new Text([{ value: 'Memory usage' }])),
        new MessageColumn(new Text([{ value: 'Message' }])),
        new ScoreColumn(new Text([{ value: 'Score' }])),
    ];

    async loadPublicContent(problem: ProblemDefinition, path: string) {
        const archive = await problem.archiveUnchecked();
        const content = await archive.fileContent(path);

        if (content === null) {
            throw unreachable(`file ${path} not found in problem ${problem.baseName} (referred from metadata)`);
        }

        this.ctx.service(FileContentService).expose(content);

        return content;
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
