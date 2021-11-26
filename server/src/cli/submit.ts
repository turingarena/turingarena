import { Submit } from '../core/submit';
import { ApiContext } from '../main/api-context';

/**
 * Inserts a submission in the database
 *
 * @param root Context
 * @param username Username that submits
 * @param contestId Contest to submit to
 * @param problemName Problem name to submit
 * @param solutionPath Path of the submission file
 */
export async function submitLocalFile(
    ctx: ApiContext,
    username: string,
    contestId: string,
    problemName: string,
    solutionPath: string,
) {
    await Submit.submit({ username, contestId, problemName, files: [] }, ctx, solutionPath);
}
