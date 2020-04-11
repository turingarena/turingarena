import { gql } from 'apollo-server-core';
import { DateTime } from 'luxon';
import * as mime from 'mime-types';
import { Op } from 'sequelize';
import { AllowNull, Column, DataType, ForeignKey, Index, Table, Unique } from 'sequelize-typescript';
import { __generated_ContestStatus } from '../generated/graphql-types';
import { ApiObject } from '../main/api';
import { createByIdLoader, createSimpleLoader, UuidBaseModel } from '../main/base-model';
import { Resolvers } from '../main/resolver-types';
import { ContestProblemAssignmentApi } from './contest-problem-assignment';
import { ContestProblemSet } from './contest-problem-set';
import { FileCollection } from './file-collection';
import { Media, MediaVariant } from './material/media';
import { ProblemMaterial, ProblemMaterialApi } from './material/problem-material';

export const contestSchema = gql`
    type Contest {
        name: ID!
        title: Text!

        "Statement of this contest, presented as its home page"
        statement: Media!

        start: String!
        end: String!
        status: ContestStatus!
        problemSet: ContestProblemSet!
        fileCollection: FileCollection!
    }

    input ContestInput {
        name: ID!
        title: String!
        start: String!
        end: String!
    }

    enum ContestStatus {
        NOT_STARTED
        RUNNING
        ENDED
    }
`;

/** A contest in TuringArena */
@Table
export class Contest extends UuidBaseModel<Contest> {
    /** Name of the contest, must be a valid identifier, e.g. ioi */
    @Unique
    @Index
    @AllowNull(false)
    @Column
    name!: string;

    /** Title of the contest, as a string, e.g. 'International Olimpics in Informatics' */
    @AllowNull(false)
    @Column
    title!: string;

    /** When the contest will start */
    @AllowNull(false)
    @Column
    start!: Date;

    /** When the contest will end */
    @AllowNull(false)
    @Column
    end!: Date;

    @AllowNull(false)
    @Column(DataType.UUIDV4)
    @ForeignKey(() => FileCollection)
    fileCollectionId!: string;

    /** supported languages, e.g [C, C++, Python2] */
    @Column(DataType.JSON)
    languages!: string[];
}

export type ContestStatus = __generated_ContestStatus;

export interface MutationModelRecord {
    Mutation: {};
}

export interface ContestModelRecord {
    Contest: Contest;
}

export class ContestApi extends ApiObject {
    byId = createByIdLoader(this.ctx, Contest);
    byName = createSimpleLoader((name: string) => this.ctx.table(Contest).findOne({ where: { name } }));

    getStatus(c: Contest): ContestStatus {
        const start = DateTime.fromJSDate(c.start).valueOf();
        const end = DateTime.fromJSDate(c.end).valueOf();
        const now = DateTime.local().valueOf();

        if (now < start) return 'NOT_STARTED';
        else if (now < end) return 'RUNNING';
        else return 'NOT_STARTED';
    }

    async getProblemSetMaterial(c: Contest): Promise<ProblemMaterial[]> {
        const assignments = await this.ctx.api(ContestProblemAssignmentApi).allByContestId.load(c.id);

        return Promise.all(assignments.map(async a => this.ctx.api(ProblemMaterialApi).byProblemId.load(a.problemId)));
    }

    private statementVariantFromFile(archiveFile: FileCollection): MediaVariant {
        const type = mime.lookup(archiveFile.path);

        return {
            name: archiveFile.path,
            type: type !== false ? type : 'application/octet-stream',
            content: () => archiveFile.getContent(),
        };
    }

    async getStatement(c: Contest): Promise<Media> {
        const statementFiles = await this.ctx.table(FileCollection).findAll({
            where: {
                uuid: c.fileCollectionId,
                path: {
                    [Op.like]: 'home%',
                },
            },
        });

        return statementFiles.map((archiveFile): MediaVariant => this.statementVariantFromFile(archiveFile));
    }
}

export const contestResolvers: Resolvers = {
    Contest: {
        name: c => c.name,
        title: c => [{ value: c.title }],
        start: c => DateTime.fromJSDate(c.start).toISO(),
        end: c => DateTime.fromJSDate(c.end).toISO(),
        status: (c, {}, ctx) => ctx.api(ContestApi).getStatus(c),
        problemSet: c => new ContestProblemSet(c),
        fileCollection: c => ({ uuid: c.fileCollectionId }),
        statement: (c, {}, ctx) => ctx.api(ContestApi).getStatement(c),
    },
};
