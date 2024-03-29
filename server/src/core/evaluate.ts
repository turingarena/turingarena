import { TaskMaker, UIMessage } from '@edomora97/task-maker';
import * as fs from 'fs';
import * as path from 'path';
import { tap, toArray } from 'rxjs/operators';
import { ApiContext } from '../main/api-context';
import { Service } from '../main/service';
import { unreachable } from '../util/unreachable';
import { EvaluationData } from './evaluation';
import { OutcomeData } from './outcome';
import { ProblemMaterialCache } from './problem-definition-material';
import { Submission } from './submission';

export interface LiveEvaluation {
    submissionId: string;
    events: UIMessage[];
}

export class LiveEvaluationService extends Service {
    liveEvaluations = new Map<string, LiveEvaluation>();

    run() {
        return () => {
            console.log(`closing`);
        };
    }

    add(evaluation: LiveEvaluation) {
        this.liveEvaluations.set(evaluation.submissionId, evaluation);
    }

    remove(evaluation: LiveEvaluation) {
        this.liveEvaluations.delete(evaluation.submissionId);
    }

    getBySubmission(submissionId: string) {
        return this.liveEvaluations.get(submissionId) ?? null;
    }
}

/**
 * Evaluate a new submission
 *
 * @param submission Submission to evaluate
 */
export async function evaluateSubmission(ctx: ApiContext, submission: Submission) {
    console.log(`Evaluating submission ${submission.id}`);

    const user = await submission.user();
    const problemUndertaking = await submission.getUndertaking();
    const problemDefinition = problemUndertaking.instance.definition;
    const problemArchive = await problemDefinition.archiveUnchecked();
    const submittedAt = await submission.createdAt();
    const material = await ctx.cache(ProblemMaterialCache).byId.load(problemDefinition.id);

    const submissionPath = await submission.extract(path.join(ctx.config.cachePath, 'submission'));

    const filepath = fs.readdirSync(submissionPath)[0];
    const solutionPath = path.join(submissionPath, filepath);
    const taskMaker = new TaskMaker(ctx.config.taskMaker);

    const { child, lines } = taskMaker.evaluate({
        taskDir: problemArchive.dir,
        solution: solutionPath,
    });

    const liveEvaluation: LiveEvaluation = { submissionId: submission.id, events: [] };

    const evaluationService = ctx.service(LiveEvaluationService);
    evaluationService.add(liveEvaluation);

    try {
        const events = await lines
            .pipe(
                tap(event => {
                    liveEvaluation.events.push(event);
                }),
                toArray(),
            )
            .toPromise();

        const output = await child;

        if (output.code !== 0) throw unreachable(`task maker return code was not zero`);

        await ctx.db.transaction(async t => {
            const evaluation = await ctx.table(EvaluationData).create({
                submissionId: submission.id,
                eventsJson: JSON.stringify(events),
                problemArchiveHash: problemArchive.hash,
            });

            for (const objective of material.objectives) {
                for (const event of events) {
                    if (!(typeof event === 'object' && 'IOISubtaskScore' in event)) continue;

                    const { subtask, normalized_score, score } = event.IOISubtaskScore;
                    if (subtask !== objective.index) continue;
                    if (normalized_score === 0) continue;

                    await ctx.table(OutcomeData).create({
                        problemId: problemUndertaking.instance.id,
                        userId: user.id,
                        submissionId: submission.id,
                        submittedAt,
                        problemHash: problemArchive.hash,
                        evaluationId: evaluation.id,
                        evaluatedAt: evaluation.createdAt,
                        objectiveIndex: subtask,
                        grade: objective.gradeDomain.__typename === 'FulfillmentGradeDomain' ? normalized_score : score,
                        isRanked: true,
                    });
                }
            }
        });
    } finally {
        evaluationService.remove(liveEvaluation);
    }
}
