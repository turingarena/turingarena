import { gql } from 'apollo-server-core';
import { Resolvers } from '../generated/graphql-types';
import { Contest, contestResolvers, contestSchema } from './contest';
import { contestAwardAssignmentResolvers, contestAwardAssignmentSchema } from './contest-award-assignment';
import { contestAwardAssignmentViewResolvers, contestAwardAssignmentViewSchema } from './contest-award-assignment-view';
import { ContestFile } from './contest-file';
import {
    ContestProblemAssignment,
    contestProblemAssignmentResolvers,
    contestProblemAssignmentSchema,
} from './contest-problem-assignment';
import {
    contestProblemAssignmentViewResolvers,
    contestProblemAssignmentViewSchema,
} from './contest-problem-assignment-view';
import { contestProblemSetResolvers, contestProblemSetSchema } from './contest-problem-set';
import { contestProblemSetViewResolvers, contestProblemSetViewSchema } from './contest-problem-set-view';
import { contestViewResolvers, contestViewSchema } from './contest-view';
import { Evaluation, evaluationSchema } from './evaluation';
import { EvaluationEvent } from './evaluation-event';
import { feedbackSlotSchema } from './feedback/feedback-slot';
import { valenceSchema } from './feedback/valence';
import { FileContent, fileContentResolvers, fileContentSchema } from './file-content';
import { gradingSchema } from './grading/grading';
import { booleanGradingSchema } from './grading/grading-boolean';
import { genericGradingSchema } from './grading/grading-generic';
import { numericGradingSchema } from './grading/grading-numeric';
import { mainViewResolvers, mainViewSchema } from './main-view';
import { awardResolvers, awardSchema } from './material/award';
import { mediaResolvers, mediaSchema } from './material/media';
import { problemMaterialSchema } from './material/problem-material';
import { textResolvers, textSchema } from './material/text';
import { mutationResolvers, mutationSchema } from './mutation';
import { Participation, participationSchema } from './participation';
import { Problem, problemResolvers, problemSchema } from './problem';
import { ProblemFile, problemFileResolvers, problemFileSchema } from './problem-file';
import { queryResolvers, querySchema } from './query';
import { Submission, submissionResolvers, submissionSchema } from './submission';
import { SubmissionFile, submissionFileSchema } from './submission-file';
import { User, userResolvers, userSchema } from './user';

/** Full GraphQL schema document. Obtained combining schema parts from each components. */
export const schema = gql`
    ${querySchema}
    ${mutationSchema}
    ${userSchema}
    ${contestSchema}
    ${participationSchema}
    ${problemSchema}
    ${problemFileSchema}
    ${awardSchema}
    ${fileContentSchema}
    ${submissionSchema}
    ${submissionFileSchema}
    ${evaluationSchema}

    ${contestProblemSetSchema}
    ${contestProblemAssignmentSchema}
    ${contestAwardAssignmentSchema}

    ${mainViewSchema}
    ${contestViewSchema}
    ${contestProblemSetViewSchema}
    ${contestProblemAssignmentViewSchema}
    ${contestAwardAssignmentViewSchema}

    ${textSchema}
    ${mediaSchema}
    ${problemMaterialSchema}

    ${genericGradingSchema}
    ${numericGradingSchema}
    ${booleanGradingSchema}
    ${gradingSchema}

    ${feedbackSlotSchema}
    ${valenceSchema}

    enum Ok {
        OK
    }
`;

/** All model classes constructors. */
export const modelConstructors = {
    User,
    Contest,
    Problem,
    ContestProblemAssignment,
    Participation,
    FileContent,
    ProblemFile,
    ContestFile,
    Submission,
    SubmissionFile,
    Evaluation,
    EvaluationEvent,
};

/** All GraphQL resolvers. Obtained combining resolvers from each components. */
export const resolvers: Resolvers = {
    ...queryResolvers,
    ...mutationResolvers,
    ...userResolvers,
    ...contestResolvers,
    ...problemResolvers,
    ...problemFileResolvers,
    ...awardResolvers,
    ...fileContentResolvers,
    ...submissionResolvers,

    ...contestProblemAssignmentResolvers,
    ...contestProblemSetResolvers,
    ...contestAwardAssignmentResolvers,

    ...mainViewResolvers,
    ...contestViewResolvers,
    ...contestProblemSetViewResolvers,
    ...contestProblemAssignmentViewResolvers,
    ...contestAwardAssignmentViewResolvers,

    ...textResolvers,
    ...mediaResolvers,
};
