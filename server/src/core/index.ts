import { gql } from 'apollo-server-core';
import { Resolvers } from '../generated/graphql-types';
import { Achievement } from './achievement';
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
    contestProblemAssignmentUserTacklingResolvers,
    contestProblemAssignmentUserTacklingSchema,
} from './contest-problem-assignment-user-tackling';
import {
    contestProblemAssignmentViewResolvers,
    contestProblemAssignmentViewSchema,
} from './contest-problem-assignment-view';
import { contestProblemSetResolvers, contestProblemSetSchema } from './contest-problem-set';
import {
    contestAssignmentUserTacklingResolvers,
    contestProblemSetUserTacklingSchema,
} from './contest-problem-set-user-tackling';
import { contestProblemSetViewResolvers, contestProblemSetViewSchema } from './contest-problem-set-view';
import { contestViewResolvers, contestViewSchema } from './contest-view';
import { Evaluation, evaluationSchema } from './evaluation';
import { EvaluationEvent } from './evaluation-event';
import { fulfillmentResolvers, fulfillmentSchema } from './feedback/fulfillment';
import { gradeResolvers, gradeSchema } from './feedback/grade';
import { memoryUsageSchema } from './feedback/memory-usage';
import { messageSchema } from './feedback/message';
import { scoreResolvers, scoreSchema } from './feedback/score';
import { timeUsageSchema } from './feedback/time-usage';
import { valenceSchema } from './feedback/valence';
import { fieldSchema } from './feedback/field';
import { FileContent, fileContentResolvers, fileContentSchema } from './file-content';
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
    ${contestProblemSetUserTacklingSchema}
    ${contestProblemAssignmentViewSchema}
    ${contestProblemAssignmentUserTacklingSchema}
    ${contestAwardAssignmentViewSchema}

    ${textSchema}
    ${mediaSchema}
    ${problemMaterialSchema}

    ${fieldSchema}
    ${gradeSchema}
    ${scoreSchema}
    ${fulfillmentSchema}
    ${messageSchema}
    ${valenceSchema}
    ${timeUsageSchema}
    ${memoryUsageSchema}

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
    Achievement,
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
    ...contestAssignmentUserTacklingResolvers,
    ...contestProblemSetViewResolvers,
    ...contestProblemAssignmentViewResolvers,
    ...contestAwardAssignmentViewResolvers,
    ...contestProblemAssignmentUserTacklingResolvers,

    ...textResolvers,
    ...mediaResolvers,

    ...gradeResolvers,
    ...scoreResolvers,
    ...fulfillmentResolvers,
};
