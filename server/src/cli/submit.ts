import { ContestCache } from '../core/contest';
import { Submit } from '../core/submit';
import { ApiContext } from '../main/api-context';

/**
 * Inserts a submission in the database
 *
 * @param root Context
 * @param username Username that submits
 * @param contestName Contest name to submit to
 * @param problemName Problem name to submit
 * @param solutionPath Path of the submission file
 */
export async function submitLocalFile(
    ctx: ApiContext,
    username: string,
    contestName: string,
    problemName: string,
    solutionPath: string,
) {
    const contest = await ctx.cache(ContestCache).byName.load(contestName);
    await Submit.submit({ username, contestId: contest.id, problemName, files: [] }, ctx, solutionPath);
}
