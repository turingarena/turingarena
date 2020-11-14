import { gql } from 'apollo-server-core';
import { sign, verify } from 'jsonwebtoken';
import { ApiEnvironment, LocalApiContext } from '../main/api-context';
import { loadConfig } from '../main/config';
import { Contest } from './contest';
import { User, UserApi } from './user';

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

/**
 * Structure of the JsonWebToken
 */
interface TokenPayload {
    contestId: string;
    username: string;
    role: string;
}

export class AuthService {
    constructor(readonly env: ApiEnvironment) {}

    ctx = new LocalApiContext(this.env);

    /**
     * Generate the response for a request of login.
     * It checks if exist in the default contest a user with the same token (secret)
     * that is passed as parameter.
     * @param token Unique secret that identify  the user
     * @returns A structure that contains the username of the user and the JsonWebToken TokenPayload generated and signed if token is valid,
     *  null otherwise
     */
    async logIn(token: string): Promise<AuthResult | null> {
        // FIXME: assuming only one contest here
        const contest = await Contest.getDefault(this.ctx);
        if (contest === null) return null;

        const user = await this.ctx.api(UserApi).getUserByToken(contest, token);
        if (user === null) return null;
        //Get the role of the user. If the role is undefined it will use 'user' isntread
        let role = (await this.ctx.api(UserApi).metadataLoader.load(user)).role;
        if (role === undefined) role = 'user';
        const payload: TokenPayload = { contestId: contest.id, username: user.username, role };

        return { user, token: sign(payload, this.ctx.environment.config.secret) };
    }

    async auth(token: string) {
        const payload = verify(token, this.ctx.environment.config.secret) as TokenPayload;

        const contest = await Contest.getDefault(this.ctx);
        if (contest === null || contest.id !== payload.contestId) {
            throw new Error(`token not valid for current contest`);
        }

        const user = await new User(contest, payload.username).validate(this.ctx);

        return user;
    }
}

/**
 * Tell if the the request is made by a logged user.
 * To check if the request is legit it looks at the field authorization of the header
 * and it verifies that the JsonWebToken in it is signed with the server password.
 * @param req Request that received
 * @returns true if the JsonWebToken received in the header is legit, false otherwise
 */
export function isLogged(req): boolean {
    const bearerHeader = req.headers['authorization']; //extract the Bearer from the header
    if (typeof bearerHeader !== 'undefined') {
        // bearerHeader = "bearer <token>" so it split the string on the space and take the second part
        const bearerToken = bearerHeader.split(' ')[1];

        try {
            const config = loadConfig();

            //if the JsonWebToken is correctly signed return true
            verify(bearerToken, config.secret); //FIXME: fix the hardocded secret

            return true;
        } catch (err) {
            //Else return false and print the error
            console.log(err.name);

            return false;
        }
    } else {
        // if the bearer header is not present the user is certainly not logged
        return false;
    }
}
