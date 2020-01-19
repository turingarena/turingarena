import { gql } from 'apollo-server-core';
import {
    BelongsTo,
    Column,
    ForeignKey,
    Model,
    PrimaryKey,
    Table,
} from 'sequelize-typescript';
import { ResolversWithModels } from '../main/resolver-types';
import { Contest } from './contest';
import { Problem } from './problem';

export const contestProblemSchema = gql`
    type ContestProblem {
        problem: Problem!
    }
`;

/** Contest to Problem N-N relation */
@Table({ timestamps: false })
export class ContestProblem extends Model<ContestProblem> {
    @ForeignKey(() => Problem)
    @PrimaryKey
    @Column
    problemId!: number;

    @ForeignKey(() => Contest)
    @PrimaryKey
    @Column
    contestId!: number;

    @BelongsTo(() => Contest)
    contest!: Contest;

    @BelongsTo(() => Problem)
    problem!: Problem;
    getProblem!: () => Promise<Problem>;
}

export const contestProblemResolvers: ResolversWithModels<{
    ContestProblem: ContestProblem;
}> = {
    ContestProblem: {
        problem: contestProblem => contestProblem.getProblem(),
    },
};
