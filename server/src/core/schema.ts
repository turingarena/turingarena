import { gql } from 'apollo-server-core';
import { outcomeSchema } from './outcome';
import { authSchema } from './auth';
import { contestSchema } from './contest';
import { objectiveInstanceSchema } from './objective-instance';
import { problemInstanceSchema } from './problem-instance';
import { problemTacklingSchema } from './problem-tackling';
import { problemSetSchema } from './problem-set-definition';
import { problemSetTacklingSchema } from './problem-set-tackling';
import { evaluationSchema } from './evaluation';
import { fieldSchema } from './data/field';
import { fulfillmentSchema } from './data/fulfillment';
import { gradeSchema } from './data/grade';
import { headerSchema } from './data/header';
import { memoryUsageSchema } from './data/memory-usage';
import { messageFieldSchema } from './data/message';
import { scoreSchema } from './data/score';
import { timeUsageSchema } from './data/time-usage';
import { valenceSchema } from './data/valence';
import { archiveSchema } from './files/archive';
import { fileContentSchema } from './files/file-content';
import { objectiveSchema } from './objective-definition';
import { mediaSchema } from './data/media';
import { problemMaterialSchema } from './problem-definition-material';
import { textSchema } from './data/text';
import { messageSchema } from './message';
import { mutationSchema } from './mutation';
import { participationSchema } from './participation';
import { problemSchema } from './problem-definition';
import { querySchema } from './query';
import { submissionSchema } from './submission';
import { submissionFileSchema } from './submission-file';
import { userSchema } from './user';
import { dateTimeSchema } from './util/date-time';
import { objectiveViewSchema } from './objective-view';
import { problemViewSchema } from './problem-view';
import { problemSetViewSchema } from './problem-set-view';
import { contestViewSchema } from './contest-view';
import { mainViewSchema } from './main-view';

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
