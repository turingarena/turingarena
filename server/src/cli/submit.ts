import { SubmitApi } from '../core/submit';
import { ApiObject } from '../main/api';

export class LocalSubmitApi extends ApiObject {
    /**
     * Inserts a submission in the database
     *
     * @param root Context
     * @param username Username that submits
     * @param contestName Contest name to submit to
     * @param problemName Problem name to submit
     * @param solutionPath Path of the submission file
     */
    async submitLocalFile(username: string, contestName: string, problemName: string, solutionPath: string) {
        await this.ctx.api(SubmitApi).submit(
            {
                username,
                contestName,
                problemName,
                files: [],
            },
            solutionPath,
        );
    }
}
