import { gql } from 'apollo-server-core';
import { Resolvers } from '../main/resolver-types';
import { ContestApi, ContestData } from './contest';
import { MessageApi } from './message';
import { Submission, SubmissionApi} from './submission';
import { User, UserApi } from './user';
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
            if (username !== null && username !== undefined) {
                await ctx.authorizeUser(username);
            }

            const contest = await ctx.api(ContestApi).getDefault();

            if (contest === null) throw new Error(`missing 'default' contest (not supported right now)`);

            return new MainView(
                contest,
                username !== null && username !== undefined
                    ? await ctx.api(UserApi).validate(new User(contest, username))
                    : null,
            );
        },
        contests: async ({}, {}, ctx) => {
            await ctx.authorizeAdmin();

            return (await ctx.table(ContestData).findAll()).map(d => ctx.api(ContestApi).fromData(d))
        },
        archive: async (_, { uuid }, ctx) => {
            await ctx.authorizeAdmin();

            return ({ uuid })
        },
        submission: async ({}, { id }, ctx) => {
            const sub = await ctx.api(SubmissionApi).validate(new Submission(id));

            // Get the username of who had made the submission and verify if
            // the current user has teh permission to made the query.
            // The query is valid if is made by the owner or by an admin user.
            const username = (await ctx.api(SubmissionApi).getTackling(sub)).user.username;
            await ctx.authorizeUser(username);

            return sub;
        },
        fileContent: async ({}, {}, ctx) => ctx.fail(`not implemented`),
        message: async ({}, { id }, ctx) => {
            //TODO: Add the possibility for who received and for who sended the message to use this query
            await ctx.authorizeAdmin();

            return ctx.api(MessageApi).fromId(id);
        },
        messages: async ({}, { id }, ctx) => {
            await ctx.authorizeUser(id);

            return ctx.api(MessageApi).find(id);
        },
    },
};
