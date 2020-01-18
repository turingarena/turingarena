import {
    BelongsToMany,
    Column,
    Index,
    Model,
    Table,
    Unique,
} from 'sequelize-typescript';
import { Contest, Participation } from './contest';

/** A user in TuringArena */
@Table
export class User extends Model<User> {
    /** Username that is used to identify the user, e.g. alerighi */
    @Unique
    @Index
    @Column
    username!: string;

    /** Full name of the user, e.g. Mario Rossi */
    @Column
    name!: string;

    /** Login token of the user, must be unique for each user, e.g. fjdkah786 */
    @Unique
    @Index
    @Column
    token!: string;

    /** Privilege of the user */
    @Column
    privilege!: UserPrivilege;

    /** Contest wich the user belongs to */
    @BelongsToMany(
        () => Contest,
        () => Participation,
    )
    contests!: Contest[];
}

/** Privilege of a user */
export enum UserPrivilege {
    /** Normal user, can take part in a contest */
    USER,
    /** Admin user, can do everything */
    ADMIN,
}
