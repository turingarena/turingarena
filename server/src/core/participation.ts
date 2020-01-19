import { BelongsTo, Column, ForeignKey, Model, PrimaryKey, Table } from 'sequelize-typescript';
import { Contest } from './contest';
import { User } from './user';

/** User participation relation */
@Table({ timestamps: false })
export class Participation extends Model<Participation> {
    @ForeignKey(() => User)
    @PrimaryKey
    @Column
    userId!: number;

    @ForeignKey(() => Contest)
    @PrimaryKey
    @Column
    contestId!: number;

    @BelongsTo(() => Contest)
    contest!: Contest;

    @BelongsTo(() => User)
    user!: User;
}
