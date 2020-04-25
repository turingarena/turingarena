import { gql } from 'apollo-server-core';
import { Resolvers } from '../main/resolver-types';
import { ContestApi, ContestData } from './contest';
import { MessageApi } from './message';
import { SubmissionApi } from './submission';
import { UserApi } from './user';
import { MainView } from './view/main-view';

export const querySchema = gql`
    type Query {
        """
        Data visible in a front page, i.e., to contestants.
        """
        mainView("Name of the user viewing the front page, if logged in" username: ID): MainView!

        contests: [Contest!]!
        fileContent(id: ID!): FileContent!
        archive(uuid: ID!): Archive!
        submission(id: ID!): Submission!
        message(id: ID!): Message
        messages(id: ID!): [Message!]!
    }
`;

export interface QueryModelRecord {
    Query: {};
}

export const queryResolvers: Resolvers = {
    Query: {
        mainView: async ({}, { username }, ctx): Promise<MainView> => {
            const contest = await ctx.api(ContestApi).getDefault();

            if (contest === null) throw new Error(`missing 'default' contest (not supported right now)`);

            return new MainView(
                contest,
                username !== null && username !== undefined
                    ? await ctx.api(UserApi).validate({ __typename: 'User', contest, username })
                    : null,
            );
        },
        contests: async ({}, {}, ctx) =>
            (await ctx.table(ContestData).findAll()).map(d => ctx.api(ContestApi).fromData(d)),
        archive: (_, { uuid }) => ({ uuid }),
        submission: async ({}, { id }, ctx) => ctx.api(SubmissionApi).validate({ __typename: 'Submission', id }),
        fileContent: async ({}, {}, ctx) => ctx.fail(`not implemented`),
        message: async ({}, { id }, ctx) => ctx.api(MessageApi).fromId(id),
        messages: async ({}, { id }, ctx) => ctx.api(MessageApi).find(id),
    },
};
