import { gql } from 'apollo-server-core';
import { DataTypes } from 'sequelize';
import {
    BelongsTo,
    Column,
    ForeignKey,
    HasMany,
    Model,
    PrimaryKey,
    Table,
} from 'sequelize-typescript';
import { Contest } from './contest';
import { File } from './file';
import { Problem } from './problem';
import { User } from './user';

export const submissionSchema = gql`
    type Submission {
        id: ID!
        problem: Problem!
        user: User!
        contest: Contest!
        files: [SubmissionFile!]!
        createdAt: String!
        officialEvaluation: Evaluation!
        evaluations: [Evaluation!]!
    }

    type SubmissionFile {
        fieldId: ID!
        file: File!
    }

    input SubmissionInput {
        problemName: ID!
        contestName: ID!
        username: ID!
        files: [SubmissionFileInput!]!
    }

    input SubmissionFileInput {
        fieldId: ID!
        file: FileInput!
    }

    type Evaluation {
        submission: Submission!
        events: [EvaluationEvent!]!
    }

    type EvaluationEvent {
        evaluation: Evaluation!
        data: String!
    }
`;

@Table({ updatedAt: false })
export class Submission extends Model<Submission> {
    @ForeignKey(() => Problem)
    @Column
    problemId!: number;

    @ForeignKey(() => Contest)
    @Column
    contestId!: number;

    @ForeignKey(() => User)
    @Column
    userId!: number;

    @HasMany(() => SubmissionFile)
    files: SubmissionFile[];

    @HasMany(() => Evaluation)
    evaluations: Evaluation[];

    @BelongsTo(() => Contest, 'contestId')
    contest: Contest;

    @BelongsTo(() => Problem, 'problemId')
    problem: Problem;

    @BelongsTo(() => User, 'userId')
    user: User;
}

@Table({ timestamps: false })
export class SubmissionFile extends Model<SubmissionFile> {
    @ForeignKey(() => Submission)
    @PrimaryKey
    @Column
    submissionId!: number;

    @ForeignKey(() => File)
    @Column
    fileId!: number;

    @PrimaryKey
    @Column
    fieldId!: string;

    @BelongsTo(() => Submission, 'submissionId')
    submission: Submission;
}

@Table
export class Evaluation extends Model<Evaluation> {
    @ForeignKey(() => Submission)
    @Column
    submissionId!: number;

    @Column
    status!: EvaluationStatus;

    @Column
    isOfficial!: boolean;

    @BelongsTo(() => Submission, 'submissionId')
    submission!: Submission;

    @HasMany(() => EvaluationEvent)
    events!: EvaluationEvent[];
}

export enum EvaluationStatus {
    PENDING,
    SUCCESS,
    ERROR,
}

@Table({ updatedAt: false })
export class EvaluationEvent extends Model<EvaluationEvent> {
    @ForeignKey(() => Evaluation)
    @Column
    evaluationId!: number;

    @BelongsTo(() => Evaluation, 'evaluationId')
    evaluation: Evaluation;

    @Column(DataTypes.JSON)
    data!: object;
}
