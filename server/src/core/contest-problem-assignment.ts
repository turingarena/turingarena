import { gql } from 'apollo-server-core';
import { BelongsTo, Column, ForeignKey, PrimaryKey, Table } from 'sequelize-typescript';
import { BaseModel } from '../main/base-model';
import { ResolversWithModels } from '../main/resolver-types';
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

export const contestProblemAssignmentResolvers: ResolversWithModels<{
    ContestProblemAssignment: ContestProblemAssignment;
}> = {
    ContestProblemAssignment: {
        contest: assignment => assignment.getContest(),
        problem: assignment => assignment.getProblem(),
    },
};
