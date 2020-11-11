import { gql } from 'apollo-server-core';
import { Resolvers } from '../main/resolver-types';
import { Achievement, AchievementModelRecord, achievementSchema } from './achievement';
import { authSchema } from './auth';
import { ContestData, ContestModelRecord, contestSchema } from './contest';
import { ContestAwardAssignmentModelRecord, contestAwardAssignmentSchema } from './contest-award-assignment';
import { ContestProblemAssignmentModelRecord, contestProblemAssignmentSchema } from './contest-problem-assignment';
import {
    ContestProblemAssignmentUserTacklingModelRecord,
    contestProblemAssignmentUserTacklingSchema,
} from './contest-problem-assignment-user-tackling';
import { ContestProblemSetModelRecord, contestProblemSetSchema } from './contest-problem-set';
import {
    ContestProblemSetUserTacklingModelRecord,
    contestProblemSetUserTacklingSchema,
} from './contest-problem-set-user-tackling';
import { Evaluation, EvaluationModelRecord, evaluationSchema } from './evaluation';
import { EvaluationEvent } from './evaluation-event';
import { fieldSchema } from './feedback/field';
import { FulfillmentModelRecord, fulfillmentSchema } from './feedback/fulfillment';
import { gradeResolvers, gradeSchema } from './feedback/grade';
import { headerSchema } from './feedback/header';
import { memoryUsageSchema } from './feedback/memory-usage';
import { messageFieldSchema } from './feedback/message';
import { ScoreModelRecord, scoreSchema } from './feedback/score';
import { timeUsageSchema } from './feedback/time-usage';
import { valenceSchema } from './feedback/valence';
import { Archive, ArchiveModelRecord, archiveResolvers, archiveSchema } from './files/archive';
import { FileContent, FileContentModelRecord, fileContentResolvers, fileContentSchema } from './files/file-content';
import { AwardModelRecord, awardSchema } from './material/award';
import { MediaModelRecord, mediaResolvers, mediaSchema } from './material/media';
import { ProblemMaterialModelRecord, problemMaterialSchema } from './material/problem-material';
import { TextModelRecord, textResolvers, textSchema } from './material/text';
import { Message, messageSchema } from './message';
import { MutationModelRecord, mutationResolvers, mutationSchema } from './mutation';
import { ParticipationModelRecord, participationSchema } from './participation';
import { ProblemModelRecord, problemSchema } from './problem';
import { QueryModelRecord, queryResolvers, querySchema } from './query';
import { SubmissionData, SubmissionModelRecord, submissionSchema } from './submission';
import { SubmissionFile, submissionFileSchema } from './submission-file';
import { UserModelRecord, userSchema } from './user';
import { DateTimeModelRecord, dateTimeResolvers, dateTimeSchema } from './util/date-time';
import {
    ContestAwardAssignmentViewModelRecord,
    contestAwardAssignmentViewSchema,
} from './view/contest-award-assignment-view';
import {
    ContestProblemAssignmentViewModelRecord,
    contestProblemAssignmentViewSchema,
} from './view/contest-problem-assignment-view';
import {
    ContestProblemSetViewModelRecord,
    contestProblemSetViewResolvers,
    contestProblemSetViewSchema,
} from './view/contest-problem-set-view';
import { ContestViewModelRecord, contestViewSchema } from './view/contest-view';
import { MainViewModelRecord, mainViewSchema } from './view/main-view';

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
    ${archiveSchema}
    ${fileContentSchema}
    ${fulfillmentSchema}
    ${gradeSchema}
    ${headerSchema}
    ${mainViewSchema}
    ${mediaSchema}
    ${memoryUsageSchema}
    ${messageFieldSchema}
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
    ${messageSchema}

    enum Ok {
        OK
    }
`;

/** All model classes constructors. */
export const modelConstructors = {
    Achievement,
    ContestData,
    Archive,
    Evaluation,
    EvaluationEvent,
    FileContent,
    SubmissionData,
    SubmissionFile,
    Message,
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
    ArchiveModelRecord &
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
    ...contestProblemSetViewResolvers,
    ...dateTimeResolvers,
    ...fileContentResolvers,
    ...gradeResolvers,
    ...mediaResolvers,
    ...mutationResolvers,
    ...queryResolvers,
    ...textResolvers,
    ...archiveResolvers,
};
