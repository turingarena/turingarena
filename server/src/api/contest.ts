import { gql } from 'apollo-server-core';
import { Resolvers } from '../generated/graphql-types';

export const contestSchema = gql`
    type Contest {
        name: ID!
        title: String!
        start: String!
        end: String!
    }

    type ContestMutations {
        addProblem(name: ID!): Boolean
        removeProblem(name: ID!): Boolean
        addUser(username: ID!): Boolean
        removeUser(username: ID!): Boolean
        submit(username: ID!, problemName: ID!, submission: SubmissionInput!): Boolean
    }

    input ContestInput {
        name: ID!
        title: String!
        start: String!
        end: String!
    }
`;

export const contestResolvers: Resolvers = {
    Contest: {
        // TODO: resolver for start and end to return in correct ISO format
    },
    ContestMutations: {
        addProblem: async ({contest}, {name}, ctx) => {
            const problem = await ctx.db.Problem.findOne({ where: { name } });
            await contest.addProblem(problem);

            return true;
        },
        addUser: async ({contest}, {username}, ctx) => {
            const user = await ctx.db.User.findOne({ where: { username }});
            await contest.addUser(user);

            return true;
        },
    },
};
