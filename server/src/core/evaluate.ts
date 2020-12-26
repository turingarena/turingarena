import { TaskMaker } from '@edomora97/task-maker';
import * as fs from 'fs';
import * as path from 'path';
import { bufferTime, concatAll, concatMap, toArray } from 'rxjs/operators';
import { ApiObject } from '../main/api';
import { ContestApi } from './contest';
import { Evaluation, EvaluationStatus } from './evaluation';
import { EvaluationEvent } from './evaluation-event';
import { ArchiveApi } from './files/archive';
import { Submission } from './submission';

export class EvaluateApi extends ApiObject {
    /**
     * Evaluate a new submission
     *
     * @param submission Submission to evaluate
     */
    async evaluate(submission: Submission) {
        console.log(`Evaluating submission ${submission.id}`);

        const evaluation = await this.ctx.table(Evaluation).create({
            submissionId: submission.id,
            status: EvaluationStatus.PENDING,
        });

        const { assignment } = await submission.getTackling();
        const { archiveId } = await this.ctx.api(ContestApi).dataLoader.load(assignment.problem.contest.id);
        const contestDir = await this.ctx.api(ArchiveApi).extractArchive(archiveId);

        const problemDir = path.join(contestDir, assignment.problem.name);

        const submissionPath = await submission.extract(path.join(this.ctx.environment.config.cachePath, 'submission'));

        const filepath = fs.readdirSync(submissionPath)[0];
        const solutionPath = path.join(submissionPath, filepath);
        const taskMaker = new TaskMaker(this.ctx.environment.config.taskMaker);

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

                    return this.ctx.table(EvaluationEvent).bulkCreate(
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
                    je !== undefined &&
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
                await event.storeAchievements(this.ctx);
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
}
