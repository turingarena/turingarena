import { spawn } from 'child_process';
import * as path from 'path';
import * as readline from 'readline';
import { ApiContext } from '../main/context';
import { EvaluationStatus } from './evaluation';
import { extractProblemFiles } from './problem-util';
import { Submission } from './submission';

/**
 * Evaluate a new submission
 *
 * @param ctx ApiContext to use
 * @param submission Submission to evaluate
 */
export async function evaluate(ctx: ApiContext, submission: Submission) {
    console.log(`Evaluating submission ${submission.id}`);

    const evaluation = await ctx.db.Evaluation.create({
        submissionId: submission.id,
        status: EvaluationStatus.EVALUATING,
        isOfficial: false,
    });

    console.log(ctx.config);

    const problem = await (await submission.getContestProblem()).getProblem();
    const problemDir = await extractProblemFiles(ctx, problem, path.join(ctx.config.cachePath, 'problem'));


    const solutionPath = path.join(ctx.config.cachePath, 'submission');
    await submission.extract(solutionPath);

    const taskMakerArgs = ['--ui=json', '--task-dir', problemDir, '--solution', solutionPath];

    const process = spawn(ctx.config.taskMakerExecutable, taskMakerArgs);

    const stdoutLineReader = readline.createInterface(process.stdout);

    stdoutLineReader.on('line', async event => {
        console.log(`Received task-maker event ${event}`);
        await ctx.db.EvaluationEvent.create({
            evaluationId: evaluation.id,
            data: event,
        });
    });

    return new Promise(resolve => process.on('close', resolve));
}
