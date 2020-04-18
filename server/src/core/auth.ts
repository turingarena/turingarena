import { gql } from 'apollo-server-core';
import { sign, verify } from 'jsonwebtoken';
import { ApiEnvironment, LocalApiContext } from '../main/api-context';
import { ContestApi } from './contest';
import { User } from './user';

export const authSchema = gql`
    type AuthResult {
        user: User!
        token: String!
    }
`;

export interface AuthResult {
    user: User;
    token: string;
}

export interface AuthModelRecord {
    AuthResult: AuthResult;
}

interface TokenPayload {
    contestId: string;
    username: string;
}

export class AuthService {
    constructor(readonly env: ApiEnvironment) {}

    ctx = new LocalApiContext(this.env);

    async logIn(token: string): Promise<AuthResult | null> {
        // FIXME: assuming only one contest here
        const contest = await this.ctx.api(ContestApi).getDefault();
        if (contest === null) return null;

        const user = await this.ctx.api(ContestApi).getUserByToken(contest, token);
        if (user === null) return null;

        const payload: TokenPayload = { contestId: contest.id, username: user.metadata.username };

        return { user, token: sign(payload, this.ctx.environment.config.secret) };
    }

    async auth(token: string) {
        const payload = verify(token, this.ctx.environment.config.secret) as TokenPayload;

        const contest = await this.ctx.api(ContestApi).getDefault();
        if (contest === null || contest.id !== payload.contestId) {
            throw new Error(`token not valid for current contest`);
        }

        const user = await this.ctx.api(ContestApi).getUserByUsername(contest, payload.username);

        return user;
    }
}
