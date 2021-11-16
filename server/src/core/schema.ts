import { gql } from 'apollo-server-core';
import { authSchema } from './auth';
import { contestSchema } from './contest';
import { contestViewSchema } from './contest-view';
import { fieldSchema } from './data/field';
import { fulfillmentSchema } from './data/fulfillment';
import { gradeSchema } from './data/grade';
import { headerSchema } from './data/header';
import { mediaSchema } from './data/media';
import { memoryUsageSchema } from './data/memory-usage';
import { messageFieldSchema } from './data/message';
import { scoreSchema } from './data/score';
import { textSchema } from './data/text';
import { timeUsageSchema } from './data/time-usage';
import { valenceSchema } from './data/valence';
import { evaluationSchema } from './evaluation';
import { archiveSchema } from './files/archive';
import { fileContentSchema } from './files/file-content';
import { mainViewSchema } from './main-view';
import { messageSchema } from './message';
import { mutationSchema } from './mutation';
import { objectiveSchema } from './objective-definition';
import { objectiveInstanceSchema } from './objective-instance';
import { objectiveViewSchema } from './objective-view';
import { outcomeSchema } from './outcome';
import { participationSchema } from './participation';
import { problemSchema } from './problem-definition';
import { problemMaterialSchema } from './problem-definition-material';
import { problemInstanceSchema } from './problem-instance';
import { problemSetSchema } from './problem-set-definition';
import { problemSetTacklingSchema } from './problem-set-tackling';
import { problemSetViewSchema } from './problem-set-view';
import { problemTacklingSchema } from './problem-tackling';
import { problemViewSchema } from './problem-view';
import { querySchema } from './query';
import { submissionSchema } from './submission';
import { submissionFileSchema } from './submission-file';
import { userSchema } from './user';
import { dateTimeSchema } from './util/date-time';

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
