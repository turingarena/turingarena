import { sign, verify } from 'jsonwebtoken';
import { LocalApiContext } from '../main/api-context';
import { ServiceContext } from '../main/service-context';
import { AuthResult } from './auth';
import { Contest } from './contest';

/**
 * Structure of the JsonWebToken
 */
export interface TokenPayload {
    contestId: string;
    username: string;
}

export class AuthService {
    constructor(readonly ctx: ServiceContext) {}

    /* Context to run priviledged API for autentication. */
    apiCtx = new LocalApiContext(this.ctx);

    /**
     * Generate the response for a request of login.
     * It checks if exist in the default contest a user with the same token (secret)
     * that is passed as parameter.
     * @param token Unique secret that identify  the user
     * @returns A structure that contains the username of the user and the JsonWebToken TokenPayload generated and signed if token is valid,
     *  null otherwise
     */
    async logIn(token: string): Promise<AuthResult | null> {
        console.log(this.ctx.service);
        console.log(this.apiCtx.service);

        // FIXME: assuming only one contest here
        const contest = await Contest.getDefault(this.apiCtx);
        if (contest === null) return null;

        const user = await contest.getUserByToken(token);
        if (user === null) return null;

        const payload: TokenPayload = { contestId: contest.id, username: user.username };

        return { user, token: sign(payload, this.apiCtx.config.secret) };
    }

    async auth(token: string) {
        const payload = verify(token, this.apiCtx.config.secret) as TokenPayload;
        const contest = await Contest.getDefault(this.apiCtx);
        if (contest === null || contest.id !== payload.contestId) {
            throw new Error(`token not valid for current contest`);
        }
        const user = await contest.getUserByName(payload.username);

        return user;
    }
}
