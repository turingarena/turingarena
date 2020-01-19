import { BelongsTo, Column, ForeignKey, Model, PrimaryKey, Table } from 'sequelize-typescript';
import { Contest } from './contest';
import { User } from './user';

/** User participation N-N relation */
@Table({ timestamps: false })
export class Participation extends Model<Participation> {
    @ForeignKey(() => User)
    @Column({ unique: 'participation_user_contest_unique' })
    userId!: number;

    @ForeignKey(() => Contest)
    @Column({ unique: 'participation_user_contest_unique' })
    contestId!: number;

    @BelongsTo(() => Contest)
    contest!: Contest;
    getContest!: (options: object) => Promise<Contest>;

    @BelongsTo(() => User)
    user!: User;
    getUser!: (options: object) => Promise<User>;
}
