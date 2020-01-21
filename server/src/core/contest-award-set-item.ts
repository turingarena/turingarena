import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../main/resolver-types';
import { Award } from './award';
import { ContestProblemSetItem } from './contest-problem-set-item';

export const contestAwardSetItemSchema = gql`
    type ContestAwardSetItem {
        problemSetItem: ContestProblemSetItem!
        award: Award!
    }
`;

export class ContestAwardSetItem {
    constructor(readonly problemSetItem: ContestProblemSetItem, readonly award: Award) {}
}

export const contestAwardSetItemResolvers: ResolversWithModels<{
    ContestAwardSetItem: ContestAwardSetItem;
}> = {
    ContestAwardSetItem: {
        problemSetItem: ({ problemSetItem }) => problemSetItem,
        award: ({ award }) => award,
    },
};
