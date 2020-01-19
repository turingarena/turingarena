import { Evaluation, EvaluationStatus } from "./evaluation";
import { Submission } from "./submission";
import { ApiContext } from "../main/context";

/**
 * Evaluate a new submission
 *
 * @param ctx ApiContext to use
 * @param submission Submission to evaluate
 */
export async function evaluate(ctx: ApiContext, submission: Submission) {
    const evaluation = await ctx.db.Evaluation.create({
        submissionId: submission.id,
        status: EvaluationStatus.EVALUATING,
        isOfficial: false,
    });

    const problem = await (await submission.getContestProblem()).getProblem();
}
