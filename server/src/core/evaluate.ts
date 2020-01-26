import { spawn } from 'child_process';
import * as path from 'path';
import * as readline from 'readline';
import { fromEvent } from 'rxjs';
import { bufferTime, concatAll, concatMap, first, map, takeUntil, toArray } from 'rxjs/operators';
import { ModelRoot } from '../main/model-root';
import { Evaluation, EvaluationStatus } from './evaluation';
import { EvaluationEvent, TaskMakerEvent } from './evaluation-event';
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

    const submissionPath = await submission.extract(path.join(root.config.cachePath, 'submission'));

    const solutionPath = path.join(submissionPath, 'solution.cpp.cpp');
    const taskMakerArgs = ['--ui=json', '--no-statement', '--task-dir', problemDir, '--solution', solutionPath];

    const process = spawn(root.config.taskMakerExecutable, taskMakerArgs);

    const stdoutLineReader = readline.createInterface(process.stdout);

    const bufferTimeSpanMillis = 200;
    const maxBufferSize = 20;

    const [[statusCode], events] = await Promise.all([
        fromEvent<[number, NodeJS.Signals]>(process, 'close')
            .pipe(first())
            .toPromise(),
        fromEvent<string>(stdoutLineReader, 'line')
            .pipe(
                takeUntil(fromEvent(stdoutLineReader, 'close')),
                map(data => JSON.parse(data) as TaskMakerEvent),
                bufferTime(bufferTimeSpanMillis, undefined, maxBufferSize),
                concatMap(async eventsData => {
                    console.log(`Inserting ${eventsData.length} buffered events.`);

                    return root.table(EvaluationEvent).bulkCreate(
                        eventsData.map(data => ({
                            evaluationId: evaluation.id,
                            data,
                        })),
                    );
                }),
                concatAll(),
                toArray(),
            )
            .toPromise(),
    ]);

    if (statusCode === 0) {
        for (const event of events) {
            await event.storeAchievements();
        }
        await evaluation.update({
            status: EvaluationStatus.SUCCESS,
        });
    } else {
        await evaluation.update({
            status: EvaluationStatus.ERROR,
        });
    }
}
