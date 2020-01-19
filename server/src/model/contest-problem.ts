import {
    BelongsTo,
    Column,
    ForeignKey,
    Model,
    PrimaryKey,
    Table,
} from 'sequelize-typescript';
import { Contest } from './contest';
import { Problem } from './problem';

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
    contest: Contest;

    @BelongsTo(() => Problem)
    problem: Problem;
}
