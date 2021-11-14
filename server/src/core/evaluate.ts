import { TaskMaker, UIMessage } from '@edomora97/task-maker';
import * as fs from 'fs';
import * as path from 'path';
import { tap, toArray } from 'rxjs/operators';
import { ApiContext } from '../main/api-context';
import { Service } from '../main/service';
import { unreachable } from '../util/unreachable';
import { Achievement } from './achievement';
import { ContestCache } from './contest';
import { EvaluationData } from './evaluation';
import { extractArchive } from './files/archive';
import { ProblemMaterialCache } from './material/problem-material';
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

    const { assignment } = await submission.getTackling();
    const { archiveId } = await ctx.cache(ContestCache).byId.load(assignment.problem.contest.id);
    const contestDir = await extractArchive(ctx, archiveId);

    const material = await ctx.cache(ProblemMaterialCache).byId.load(assignment.problem.id());

    const problemDir = path.join(contestDir, assignment.problem.name);

    const submissionPath = await submission.extract(path.join(ctx.config.cachePath, 'submission'));

    const filepath = fs.readdirSync(submissionPath)[0];
    const solutionPath = path.join(submissionPath, filepath);
    const taskMaker = new TaskMaker(ctx.config.taskMaker);

    const { child, lines } = taskMaker.evaluate({
        taskDir: problemDir,
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
            const evaluation = await ctx
                .table(EvaluationData)
                .create({ submissionId: submission.id, eventsJson: JSON.stringify(events) });

            for (const award of material.awards) {
                for (const event of events) {
                    if (!(typeof event === 'object' && 'IOISubtaskScore' in event)) continue;

                    const { subtask, normalized_score, score } = event.IOISubtaskScore;
                    if (subtask !== award.index) continue;
                    if (normalized_score === 0) continue;

                    await ctx.table(Achievement).create({
                        evaluationId: evaluation.id,
                        awardIndex: subtask,
                        grade: award.gradeDomain.__typename === 'FulfillmentGradeDomain' ? normalized_score : score,
                    });
                }
            }
        });
    } finally {
        evaluationService.remove(liveEvaluation);
    }
}
