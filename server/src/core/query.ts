import { gql } from 'apollo-server-core';
import { ApiOutputValue } from '../main/graphql-types';
import { unreachable } from '../util/unreachable';
import { Contest } from './contest';
import { MainView } from './main-view';
import { MessageApi } from './message';
import { Submission } from './submission';

export const querySchema = gql`
    type Query {
        """
        Data visible in a front page, i.e., to contestants.
        """
        mainView("Name of the user viewing the front page, if logged in" username: ID): MainView!
        contest(id: ID!): Contest!
        fileContent(id: ID!): FileContent!
        submission(id: ID!): Submission!
        message(id: ID!): Message
        messages(id: ID!): [Message!]!
    }
`;

export const queryRoot: ApiOutputValue<'Query'> = {
    mainView: async ({ username }, ctx) => {
        if (username !== null && username !== undefined) {
            await ctx.authorizeUser(username);
        }

        const contest = await Contest.getDefault(ctx);

        if (contest === null) throw new Error(`missing 'default' contest (not supported right now)`);

        return new MainView(
            contest,
            username !== null && username !== undefined ? await contest.getUserByName(username) : null,
            ctx,
        );
    },
    submission: async ({ id }, ctx) => {
        const submission = await new Submission(id, ctx).validate();

        // Get the username of who had made the submission and verify if
        // the current user has teh permission to made the query.
        // The query is valid if is made by the owner or by an admin user.
        const username = (await submission.getUndertaking()).user.username;
        await ctx.authorizeUser(username);

        return submission;
    },
    fileContent: async () => unreachable(`not implemented`),
    message: async ({ id }, ctx) => {
        //TODO: Add the possibility for who received and for who sended the message to use this query
        await ctx.authorizeAdmin();

        return ctx.cache(MessageApi).fromId(id);
    },
    messages: async ({ id }, ctx) => {
        await ctx.authorizeUser(id);

        return ctx.cache(MessageApi).find(id);
    },
    contest: async ({ id }, ctx) => {
        await ctx.authorizeAdmin();

        return new Contest(id, ctx);
    },
};
