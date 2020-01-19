import { Contest } from './contest';
import { ContestFile } from './contest-file';
import { ContestProblem } from './contest-problem';
import { Evaluation, EvaluationEvent } from './evaluation';
import { File } from './file';
import { Participation } from './participation';
import { Problem } from './problem';
import { ProblemFile } from './problem-file';
import { Submission } from './submission';
import { SubmissionFile } from './submission-file';
import { User } from './user';

export const modelConstructors = {
    User,
    Contest,
    Problem,
    ContestProblem,
    Participation,
    File,
    ProblemFile,
    ContestFile,
    Submission,
    SubmissionFile,
    Evaluation,
    EvaluationEvent,
};
