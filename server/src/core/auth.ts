import { gql } from 'apollo-server-core';
import { sign, verify } from 'jsonwebtoken';
import { ModelRoot } from '../main/model-root';
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

export class AuthService {
    constructor(readonly root: ModelRoot) {}

    async logIn(token: string): Promise<AuthResult | null> {
        const user = await this.root.table(User).findOne({ where: { token } });
        if (user === null) return null;

        return { user, token: sign({ username: user.username }, this.root.config.secret) };
    }

    async auth(token: string) {
        const payload: any = verify(token, this.root.config.secret);

        const user = await this.root.table(User).findOne({ where: { username: payload.username }});

        return user;
    }
}
