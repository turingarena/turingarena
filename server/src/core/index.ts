import { gql } from 'apollo-server-core';
import { Resolvers } from '../main/resolver-types';
import { Achievement, AchievementModelRecord, achievementSchema } from './achievement';
import { authSchema } from './auth';
import { Contest, ContestModelRecord, contestResolvers, contestSchema } from './contest';
import {
    ContestAwardAssignmentModelRecord,
    contestAwardAssignmentResolvers,
    contestAwardAssignmentSchema,
} from './contest-award-assignment';
import {
    ContestAwardAssignmentViewModelRecord,
    contestAwardAssignmentViewResolvers,
    contestAwardAssignmentViewSchema,
} from './contest-award-assignment-view';
import {
    ContestProblemAssignment,
    ContestProblemAssignmentModelRecord,
    contestProblemAssignmentResolvers,
    contestProblemAssignmentSchema,
} from './contest-problem-assignment';
import {
    ContestProblemAssignmentUserTacklingModelRecord,
    contestProblemAssignmentUserTacklingResolvers,
    contestProblemAssignmentUserTacklingSchema,
} from './contest-problem-assignment-user-tackling';
import {
    ContestProblemAssignmentViewModelRecord,
    contestProblemAssignmentViewResolvers,
    contestProblemAssignmentViewSchema,
} from './contest-problem-assignment-view';
import {
    ContestProblemSetModelRecord,
    contestProblemSetResolvers,
    contestProblemSetSchema,
} from './contest-problem-set';
import {
    contestAssignmentUserTacklingResolvers,
    ContestProblemSetUserTacklingModelRecord,
    contestProblemSetUserTacklingSchema,
} from './contest-problem-set-user-tackling';
import {
    ContestProblemSetViewModelRecord,
    contestProblemSetViewResolvers,
    contestProblemSetViewSchema,
} from './contest-problem-set-view';
import { ContestViewModelRecord, contestViewResolvers, contestViewSchema } from './contest-view';
import { DateTimeModelRecord, dateTimeResolvers, dateTimeSchema } from './date-time';
import { Evaluation, EvaluationModelRecord, evaluationSchema } from './evaluation';
import { EvaluationEvent } from './evaluation-event';
import { fieldSchema } from './feedback/field';
import { FulfillmentModelRecord, fulfillmentResolvers, fulfillmentSchema } from './feedback/fulfillment';
import { gradeResolvers, gradeSchema } from './feedback/grade';
import { headerSchema } from './feedback/header';
import { memoryUsageSchema } from './feedback/memory-usage';
import { messageSchema } from './feedback/message';
import { ScoreModelRecord, scoreResolvers, scoreSchema } from './feedback/score';
import { timeUsageSchema } from './feedback/time-usage';
import { valenceSchema } from './feedback/valence';
import {
    FileCollection,
    FileCollectionModelRecord,
    fileCollectionResolvers,
    fileCollectionSchema,
} from './file-collection';
import { FileContent, FileContentModelRecord, fileContentResolvers, fileContentSchema } from './file-content';
import { MainViewModelRecord, mainViewResolvers, mainViewSchema } from './main-view';
import { AwardModelRecord, awardResolvers, awardSchema } from './material/award';
import { MediaModelRecord, mediaResolvers, mediaSchema } from './material/media';
import { ProblemMaterialModelRecord, problemMaterialSchema } from './material/problem-material';
import { TextModelRecord, textResolvers, textSchema } from './material/text';
import { MutationModelRecord, mutationResolvers, mutationSchema } from './mutation';
import { Participation, ParticipationModelRecord, participationSchema } from './participation';
import { Problem, ProblemModelRecord, problemResolvers, problemSchema } from './problem';
import { QueryModelRecord, queryResolvers, querySchema } from './query';
import { Submission, SubmissionModelRecord, submissionResolvers, submissionSchema } from './submission';
import { SubmissionFile, submissionFileSchema } from './submission-file';
import { User, UserModelRecord, userResolvers, userSchema } from './user';

/** Full GraphQL schema document. Obtained combining schema parts from each components. */
export const schema = gql`
    ${achievementSchema}
    ${authSchema}
    ${awardSchema}
    ${contestAwardAssignmentSchema}
    ${contestAwardAssignmentViewSchema}
    ${contestProblemAssignmentSchema}
    ${contestProblemAssignmentUserTacklingSchema}
    ${contestProblemAssignmentViewSchema}
    ${contestProblemSetSchema}
    ${contestProblemSetUserTacklingSchema}
    ${contestProblemSetViewSchema}
    ${contestSchema}
    ${contestViewSchema}
    ${dateTimeSchema}
    ${evaluationSchema}
    ${fieldSchema}
    ${fileCollectionSchema}
    ${fileContentSchema}
    ${fulfillmentSchema}
    ${gradeSchema}
    ${headerSchema}
    ${mainViewSchema}
    ${mediaSchema}
    ${memoryUsageSchema}
    ${messageSchema}
    ${mutationSchema}
    ${participationSchema}
    ${problemMaterialSchema}
    ${problemSchema}
    ${querySchema}
    ${scoreSchema}
    ${submissionFileSchema}
    ${submissionSchema}
    ${textSchema}
    ${timeUsageSchema}
    ${userSchema}
    ${valenceSchema}

    enum Ok {
        OK
    }
`;

/** All model classes constructors. */
export const modelConstructors = {
    Achievement,
    Contest,
    ContestProblemAssignment,
    FileCollection,
    Evaluation,
    EvaluationEvent,
    FileContent,
    Participation,
    Problem,
    Submission,
    SubmissionFile,
    User,
};

export type ModelRecord = unknown &
    AchievementModelRecord &
    AwardModelRecord &
    ContestAwardAssignmentModelRecord &
    ContestAwardAssignmentViewModelRecord &
    ContestModelRecord &
    ContestProblemAssignmentModelRecord &
    ContestProblemAssignmentUserTacklingModelRecord &
    ContestProblemAssignmentViewModelRecord &
    ContestProblemSetModelRecord &
    ContestProblemSetUserTacklingModelRecord &
    ContestProblemSetUserTacklingModelRecord &
    ContestProblemSetViewModelRecord &
    ContestViewModelRecord &
    DateTimeModelRecord &
    EvaluationModelRecord &
    FileCollectionModelRecord &
    FileContentModelRecord &
    FulfillmentModelRecord &
    MainViewModelRecord &
    MediaModelRecord &
    MutationModelRecord &
    ParticipationModelRecord &
    ProblemMaterialModelRecord &
    ProblemModelRecord &
    QueryModelRecord &
    ScoreModelRecord &
    SubmissionModelRecord &
    TextModelRecord &
    UserModelRecord &
    unknown;

/** All GraphQL resolvers. Obtained combining resolvers from each components. */
export const resolvers: Resolvers = {
    ...awardResolvers,
    ...contestAssignmentUserTacklingResolvers,
    ...contestAwardAssignmentResolvers,
    ...contestAwardAssignmentViewResolvers,
    ...contestProblemAssignmentResolvers,
    ...contestProblemAssignmentUserTacklingResolvers,
    ...contestProblemAssignmentViewResolvers,
    ...contestProblemSetResolvers,
    ...contestProblemSetViewResolvers,
    ...contestResolvers,
    ...contestViewResolvers,
    ...dateTimeResolvers,
    ...fileContentResolvers,
    ...fulfillmentResolvers,
    ...gradeResolvers,
    ...mainViewResolvers,
    ...mediaResolvers,
    ...mutationResolvers,
    ...problemResolvers,
    ...queryResolvers,
    ...scoreResolvers,
    ...submissionResolvers,
    ...textResolvers,
    ...userResolvers,
    ...fileCollectionResolvers,
};
