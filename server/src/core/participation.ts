import { BelongsTo, Column, ForeignKey, Model, PrimaryKey, Table } from 'sequelize-typescript';
import { Contest } from './contest';
import { User } from './user';

/** User participation N-N relation */
@Table({ timestamps: false })
export class Participation extends Model<Participation> {
    @ForeignKey(() => Contest)
    @PrimaryKey
    @Column
    contestId!: number;

    @ForeignKey(() => User)
    @PrimaryKey
    @Column
    userId!: number;

    @BelongsTo(() => Contest)
    contest!: Contest;
    getContest!: (options: object) => Promise<Contest>;

    @BelongsTo(() => User)
    user!: User;
    getUser!: (options: object) => Promise<User>;
}
