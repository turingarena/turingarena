import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../main/resolver-types';
import { ContestProblemAssignment } from './contest-problem-assignment';
import { Award } from './material/award';

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
