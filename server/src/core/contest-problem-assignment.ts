import { gql } from 'apollo-server-core';
import { BelongsTo, Column, ForeignKey, PrimaryKey, Table } from 'sequelize-typescript';
import { ApiObject } from '../main/api';
import { BaseModel, createSimpleLoader } from '../main/base-model';
import { Resolvers } from '../main/resolver-types';
import { Contest } from './contest';
import { Problem } from './problem';

export const contestProblemAssignmentSchema = gql`
    type ContestProblemAssignment {
        contest: Contest!
        problem: Problem!
    }
`;

/** Contest to Problem N-N relation */
@Table({ timestamps: false })
export class ContestProblemAssignment extends BaseModel<ContestProblemAssignment> {
    @ForeignKey(() => Problem)
    @PrimaryKey
    @Column
    problemId!: number;

    @ForeignKey(() => Contest)
    @PrimaryKey
    @Column
    contestId!: number;

    // TODO: add index to make problem order deterministic

    @BelongsTo(() => Contest)
    contest!: Contest;
    getContest!: () => Promise<Contest>;

    @BelongsTo(() => Problem)
    problem!: Problem;
    getProblem!: () => Promise<Problem>;
}

export interface ContestProblemAssignmentModelRecord {
    ContestProblemAssignment: ContestProblemAssignment;
}

export class ContestProblemAssignmentApi extends ApiObject {
    byContestAndProblem = createSimpleLoader(({ contestId, problemId }: { contestId: string; problemId: string }) =>
        this.ctx.root.table(ContestProblemAssignment).findOne({ where: { contestId, problemId } }),
    );
}

export const contestProblemAssignmentResolvers: Resolvers = {
    ContestProblemAssignment: {
        contest: assignment => assignment.getContest(),
        problem: assignment => assignment.getProblem(),
    },
};
