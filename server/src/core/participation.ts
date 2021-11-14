import { gql } from 'apollo-server-core';
import { Contest } from './contest';
import { User } from './user';

export const participationSchema = gql`
    type Participation {
        contest: Contest!
        user: User!
    }
`;

export interface Participation {
    __typename: 'Participation';
    contest: Contest;
    user: User;
}
