import { TaskMaker } from '@edomora97/task-maker';
import * as fs from 'fs';
import * as path from 'path';
import { bufferTime, concatAll, concatMap, toArray } from 'rxjs/operators';
import { ApiContext } from '../main/api-context';
import { Service } from '../main/service';
import { ContestCache } from './contest';
import { EvaluationData, EvaluationStatus } from './evaluation';
import { EvaluationEvent } from './evaluation-event';
import { extractArchive } from './files/archive';
import { Submission } from './submission';

export class EvaluationService extends Service {
    run() {
        console.log(`starting evaluation service`);

        return () => {
            console.log(`closing`);
        };
    }
}

/**
 * Evaluate a new submission
 *
 * @param submission Submission to evaluate
 */
export async function evaluateSubmission(ctx: ApiContext, submission: Submission) {
    console.log(`Evaluating submission ${submission.id}`);

    const evaluation = await ctx.table(EvaluationData).create({
        submissionId: submission.id,
        status: EvaluationStatus.PENDING,
    });

    const { assignment } = await submission.getTackling();
    const { archiveId } = await ctx.cache(ContestCache).byId.load(assignment.problem.contest.id);
    const contestDir = await extractArchive(ctx, archiveId);

    const problemDir = path.join(contestDir, assignment.problem.name);

    const submissionPath = await submission.extract(path.join(ctx.config.cachePath, 'submission'));

    const filepath = fs.readdirSync(submissionPath)[0];
    const solutionPath = path.join(submissionPath, filepath);
    const taskMaker = new TaskMaker(ctx.config.taskMaker);

    const { lines, child, stderr } = taskMaker.evaluate({
        taskDir: problemDir,
        solution: solutionPath,
    });

    const bufferTimeSpanMillis = 200;
    const maxBufferSize = 20;

    const events = await lines
        .pipe(
            bufferTime(bufferTimeSpanMillis, undefined, maxBufferSize),
            concatMap(async eventsData => {
                console.log(`Inserting ${eventsData.length} buffered events.`);

                return ctx.table(EvaluationEvent).bulkCreate(
                    eventsData.map(data => ({
                        evaluationId: evaluation.id,
                        data,
                    })),
                );
            }),
            concatAll(),
            toArray(),
        )
        .toPromise();
    let jsonEvents;
    try {
        jsonEvents = await JSON.parse(await JSON.stringify(events));
    } catch (e) {
        jsonEvents = await JSON.parse('');
        console.log(e);
    }
    let failedToCompile = false;
    jsonEvents.forEach(
        (je: {
            data: {
                Compilation:
                    | { status: string | { Done: { result: { status: string | { ReturnCode: number } } } } }
                    | undefined;
            };
        }) => {
            if (
                typeof je?.data?.Compilation?.status !== 'string' &&
                typeof je?.data?.Compilation?.status?.Done?.result?.status !== 'string' &&
                je?.data?.Compilation?.status?.Done?.result?.status?.ReturnCode === 1
            ) {
                failedToCompile = true;
            }
        },
    );

    let output;
    try {
        output = await child;
    } catch (e) {
        await evaluation.update({
            status: EvaluationStatus.ERROR,
        });
        const stderrContent = await stderr;
        console.error('task-maker failed to evaluate task:', e, stderrContent);

        return;
    }

    if (output.code === 0) {
        for (const event of events) {
            await event.storeAchievements(ctx);
        }
        await evaluation.update({
            status: failedToCompile ? EvaluationStatus.COMPILEERROR : EvaluationStatus.SUCCESS,
        });
    } else {
        await evaluation.update({
            status: EvaluationStatus.ERROR,
        });
    }
}
