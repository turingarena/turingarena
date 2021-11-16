import { gql } from 'apollo-server-core';
import { outcomeSchema } from './achievement';
import { authSchema } from './auth';
import { contestSchema } from './contest';
import { objectiveInstanceSchema } from './contest-objective-assignment';
import { problemInstanceSchema } from './contest-problem-assignment';
import { problemTacklingSchema } from './contest-problem-assignment-user-tackling';
import { problemSetSchema } from './contest-problem-set';
import { problemSetTacklingSchema } from './contest-problem-set-user-tackling';
import { evaluationSchema } from './evaluation';
import { fieldSchema } from './feedback/field';
import { fulfillmentSchema } from './feedback/fulfillment';
import { gradeSchema } from './feedback/grade';
import { headerSchema } from './feedback/header';
import { memoryUsageSchema } from './feedback/memory-usage';
import { messageFieldSchema } from './feedback/message';
import { scoreSchema } from './feedback/score';
import { timeUsageSchema } from './feedback/time-usage';
import { valenceSchema } from './feedback/valence';
import { archiveSchema } from './files/archive';
import { fileContentSchema } from './files/file-content';
import { objectiveSchema } from './material/objective';
import { mediaSchema } from './material/media';
import { problemMaterialSchema } from './material/problem-material';
import { textSchema } from './material/text';
import { messageSchema } from './message';
import { mutationSchema } from './mutation';
import { participationSchema } from './participation';
import { problemSchema } from './problem';
import { querySchema } from './query';
import { submissionSchema } from './submission';
import { submissionFileSchema } from './submission-file';
import { userSchema } from './user';
import { dateTimeSchema } from './util/date-time';
import { objectiveViewSchema } from './view/contest-objective-assignment-view';
import { problemViewSchema } from './view/contest-problem-assignment-view';
import { problemSetViewSchema } from './view/contest-problem-set-view';
import { contestViewSchema } from './view/contest-view';
import { mainViewSchema } from './view/main-view';

/** Full GraphQL schema document. Obtained combining schema parts from each components. */
export const schema = gql`
    ${outcomeSchema}
    ${archiveSchema}
    ${authSchema}
    ${objectiveSchema}
    ${objectiveInstanceSchema}
    ${objectiveViewSchema}
    ${problemInstanceSchema}
    ${problemTacklingSchema}
    ${problemViewSchema}
    ${problemSetSchema}
    ${problemSetTacklingSchema}
    ${problemSetViewSchema}
    ${contestSchema}
    ${contestViewSchema}
    ${dateTimeSchema}
    ${evaluationSchema}
    ${fieldSchema}
    ${fileContentSchema}
    ${fulfillmentSchema}
    ${gradeSchema}
    ${headerSchema}
    ${mainViewSchema}
    ${mediaSchema}
    ${memoryUsageSchema}
    ${messageFieldSchema}
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
