import { gql } from 'apollo-server-core';
import { ApiOutputValue } from '../main/graphql-types';
import { MessageApi } from './message';
import { Submit } from './submit';

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
        await ctx.environment.sequelize.sync();

        return true;
    },
    submit: async ({ submission }, ctx) => {
        await ctx.authorizeUser(submission.username);
        const submissionOutput = await Submit.submit(submission, ctx);

        return (submissionOutput as unknown) as ApiOutputValue<'Submission'>; // FIXME: types
    },
    logIn: ({ token }, ctx) => ctx.environment.authService.logIn(token),
    sendMessage: async ({ message }, ctx) => {
        if (typeof message.from === 'string') await ctx.authorizeUser(message.from);
        else await ctx.authorizeAdmin();

        return ctx.api(MessageApi).sendMessage(message);
    },
};
