import { gql } from 'apollo-server-core';
import { Column, ForeignKey, PrimaryKey, Table } from 'sequelize-typescript';
import { ApiObject } from '../main/api';
import { BaseModel, createSimpleLoader } from '../main/base-model';
import { Resolvers } from '../main/resolver-types';
import { Contest, ContestApi } from './contest';
import { Problem, ProblemApi } from './problem';

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
    problemId!: string;

    @ForeignKey(() => Contest)
    @PrimaryKey
    @Column
    contestId!: string;

    // TODO: add index to make problem order deterministic
}

export interface ContestProblemAssignmentModelRecord {
    ContestProblemAssignment: ContestProblemAssignment;
}

export class ContestProblemAssignmentApi extends ApiObject {
    byContestAndProblem = createSimpleLoader(({ contestId, problemId }: { contestId: string; problemId: string }) =>
        this.ctx.table(ContestProblemAssignment).findOne({ where: { contestId, problemId } }),
    );
    allByContestId = createSimpleLoader((contestId: string) =>
        this.ctx.table(ContestProblemAssignment).findAll({ where: { contestId } }),
    );
}

export const contestProblemAssignmentResolvers: Resolvers = {
    ContestProblemAssignment: {
        contest: ({ contestId }, {}, ctx) => ctx.api(ContestApi).byId.load(contestId),
        problem: ({ problemId }, {}, ctx) => ctx.api(ProblemApi).byId.load(problemId),
    },
};
