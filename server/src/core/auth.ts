import { gql } from 'apollo-server-core';
import { sign, verify } from 'jsonwebtoken';
import { ApiEnvironment, LocalApiContext } from '../main/api-context';
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
    username: string;
}

export class AuthService {
    constructor(readonly env: ApiEnvironment) {}

    ctx = new LocalApiContext(this.env);

    async logIn(token: string): Promise<AuthResult | null> {
        const user = await this.ctx.table(User).findOne({ where: { token } });
        if (user === null) return null;
        const payload: TokenPayload = { username: user.username };

        return { user, token: sign(payload, this.ctx.environment.config.secret) };
    }

    async auth(token: string) {
        const payload = verify(token, this.ctx.environment.config.secret) as TokenPayload;
        const user = await this.ctx.table(User).findOne({ where: { username: payload.username } });

        return user;
    }
}
