import { gql } from 'apollo-server-core';
import { ApiOutputValue } from '../main/graphql-types';
import { MessageApi } from './message';
import { submit } from './submit';

export const mutationSchema = gql`
    type Mutation {
        init: Boolean!
        submit(submission: SubmissionInput!): Submission!
        logIn(token: String!): AuthResult
        sendMessage(message: MessageInput!): Message!
    }
`;

export const mutationRoot: ApiOutputValue<'Mutation'> = {
    init: async ({}, ctx) => {
        await ctx.db.sync();

        return true;
    },
    submit: async ({ submission }, ctx) => {
        await ctx.authorizeUser(submission.username);
        return submit(submission, ctx);
    },
    logIn: ({ token }, ctx) => ctx.auth.logIn(token),
    sendMessage: async ({ message }, ctx) => {
        if (typeof message.from === 'string') await ctx.authorizeUser(message.from);
        else await ctx.authorizeAdmin();

        return ctx.cache(MessageApi).sendMessage(message);
    },
};
