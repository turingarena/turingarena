import { gql } from 'apollo-server-core';
import { BelongsTo, Column, ForeignKey, PrimaryKey, Table } from 'sequelize-typescript';
import { ApiObject } from '../main/api';
import { BaseModel, createSimpleLoader } from '../main/base-model';
import { Contest } from './contest';
import { User } from './user';

export const participationSchema = gql`
    type Participation {
        contest: Contest!
        user: User!
    }
`;

/** User participation N-N relation */
@Table({ timestamps: false })
export class Participation extends BaseModel<Participation> {
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

export interface ParticipationModelRecord {
    Participation: Participation;
}

export class ParticipationApi extends ApiObject {
    byUserAndContest = createSimpleLoader(({ userId, contestId }: { userId: string; contestId: string }) =>
        this.ctx.root.table(Participation).findOne({ where: { contestId, userId } }),
    );
}
