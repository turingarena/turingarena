import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../main/resolver-types';
import { Contest } from './contest';
import { User } from './user';

export const contestViewSchema = gql`
    type ContestView {
        contest: Contest!
        user: User

        # problemSet: ProblemSet
    }
`;

export interface ContestView {
    contest: Contest;
    user: User | null;
}

export const contestViewResolvers: ResolversWithModels<{
    ContestView: ContestView;
}> = {
    ContestView: {
        contest: ({ contest }) => contest,
        user: ({ user }) => user,
    },
};
