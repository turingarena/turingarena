import { submit } from '../core/submit';
import { ModelRoot } from '../main/model-root';

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
    root: ModelRoot,
    username: string,
    contestName: string,
    problemName: string,
    solutionPath: string,
) {
    await submit(
        root,
        {
            username,
            contestName,
            problemName,
            files: [],
        },
        solutionPath,
    );
}
