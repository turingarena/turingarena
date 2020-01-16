import { gql } from 'apollo-server-core';
import { BelongsToMany, Column, HasMany, Model, Table } from 'sequelize-typescript';
import { Contest, ContestProblem } from './contest';

export const problemSchema = gql`
    type Problem {
        name: ID!
    }

    input ProblemInput {
        name: ID!
    }
`;

@Table
export class Problem extends Model<Problem> {
    @Column({ primaryKey: true, autoIncrement: true })
    id!: number;

    @Column({unique: true})
    name!: string;

    @BelongsToMany(() => Contest, () => ContestProblem)
    problems: Contest[];
}
