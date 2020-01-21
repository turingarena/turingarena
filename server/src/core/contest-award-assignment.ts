import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../main/resolver-types';
import { Award } from './award';
import { ContestProblemAssignment } from './contest-problem-assignment';

export const contestAwardAssignmentSchema = gql`
    type ContestAwardAssignment {
        problemAssignment: ContestProblemAssignment!
        award: Award!
    }
`;

export class ContestAwardAssignment {
    constructor(readonly problemAssignment: ContestProblemAssignment, readonly award: Award) {}
}

export const contestAwardAssignmentResolvers: ResolversWithModels<{
    ContestAwardAssignment: ContestAwardAssignment;
}> = {
    ContestAwardAssignment: {
        problemAssignment: ({ problemAssignment }) => problemAssignment,
        award: ({ award }) => award,
    },
};
