import { spawn } from 'child_process';
import * as path from 'path';
import * as readline from 'readline';
import { fromEvent } from 'rxjs';
import { bufferTime, concatMap, takeUntil, tap } from 'rxjs/operators';
import { ModelRoot } from '../main/model-root';
import { Evaluation, EvaluationStatus } from './evaluation';
import { EvaluationEvent } from './evaluation-event';
import { extractProblemFiles } from './material/problem-task-info';
import { Submission } from './submission';

/**
 * Evaluate a new submission
 *
 * @param root model root
 * @param submission Submission to evaluate
 */
export async function evaluate(root: ModelRoot, submission: Submission) {
    console.log(`Evaluating submission ${submission.id}`);

    const evaluation = await root.table(Evaluation).create({
        submissionId: submission.id,
        status: EvaluationStatus.PENDING,
        isOfficial: false,
    });

    console.log(root.config);

    const problem = await submission.getProblem();
    const problemDir = await extractProblemFiles(problem, path.join(root.config.cachePath, 'problem'));

    const solutionPath = path.join(root.config.cachePath, 'submission');
    await submission.extract(solutionPath);

    const taskMakerArgs = ['--ui=json', '--task-dir', problemDir, '--solution', solutionPath];

    const process = spawn(root.config.taskMakerExecutable, taskMakerArgs);

    const stdoutLineReader = readline.createInterface(process.stdout);

    const bufferTimeSpanMillis = 200;
    const maxBufferSize = 20;

    await fromEvent(stdoutLineReader, 'line')
        .pipe(
            takeUntil(fromEvent(stdoutLineReader, 'close')),
            tap(event => {
                console.log(`Received task-maker event ${event}`);
            }),
            bufferTime(bufferTimeSpanMillis, undefined, maxBufferSize),
            concatMap(async events => {
                console.log(`Inserting ${events.length} buffered events.`);
                await root.table(EvaluationEvent).bulkCreate(
                    events.map(data => ({
                        evaluationId: evaluation.id,
                        data,
                    })),
                );
            }),
        )
        .toPromise();

    const statusCode: number = await new Promise(resolve => process.on('close', resolve));

    if (statusCode === 0) {
        await evaluation.update({
            status: EvaluationStatus.SUCCESS,
        });
    } else {
        await evaluation.update({
            status: EvaluationStatus.ERROR,
        });
    }
}
