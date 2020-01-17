import { Contest, ContestFile, ContestProblem, Participation } from './contest';
import { Evaluation, EvaluationEvent } from './evaluation';
import { File } from './file';
import { Problem, ProblemFile } from './problem';
import { Submission, SubmissionFile } from './submission';
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
} as const;
