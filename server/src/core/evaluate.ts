import { spawn } from 'child_process';
import * as path from 'path';
import * as readline from 'readline';
import { fromEvent } from 'rxjs';
import { bufferTime, concatAll, concatMap, first, map, takeUntil, toArray } from 'rxjs/operators';
import { ApiObject } from '../main/api';
import { Evaluation, EvaluationStatus } from './evaluation';
import { EvaluationEvent, EvaluationEventApi, TaskMakerEvent } from './evaluation-event';
import { ArchiveApi } from './files/archive';
import { ProblemApi } from './problem';
import { Submission, SubmissionApi } from './submission';

export class EvaluateApi extends ApiObject {
    /**
     * Evaluate a new submission
     *
     * @param root model root
     * @param submission Submission to evaluate
     */
    async evaluate(submission: Submission) {
        console.log(`Evaluating submission ${submission.id}`);

        const evaluation = await this.ctx.table(Evaluation).create({
            submissionId: submission.id,
            status: EvaluationStatus.PENDING,
        });

        console.log(this.ctx.environment.config);

        const problem = await this.ctx.api(ProblemApi).byId.load(submission.problemId);
        const problemDir = await this.ctx.api(ArchiveApi).extractArchive(problem.archiveId);

        const submissionPath = await this.ctx
            .api(SubmissionApi)
            .extract(submission, path.join(this.ctx.environment.config.cachePath, 'submission'));

        const solutionPath = path.join(submissionPath, 'solution.cpp.cpp');
        const taskMakerArgs = ['--ui=json', '--no-statement', '--task-dir', problemDir, '--solution', solutionPath];

        let process;
        try {
            process = spawn(this.ctx.environment.config.taskMakerExecutable, taskMakerArgs);
        } catch (e) {
            await evaluation.update({
                status: EvaluationStatus.ERROR,
            });

            console.error(`TaskMaker executable  ${this.ctx.environment.config.taskMakerExecutable} not found`);

            return;
        }

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
                .toPromise(),
        ]);

        if (statusCode === 0) {
            for (const event of events) {
                await this.ctx.api(EvaluationEventApi).storeAchievements(event);
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
}
