import { gql } from 'apollo-server-core';

export const participationSchema = gql`
    type Participation {
        contest: Contest!
        user: User!
    }
`;

export class Participation {
    constructor(readonly contestId: string, readonly username: string) {}
}

export interface ParticipationModelRecord {
    Participation: Participation;
}
