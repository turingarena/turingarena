import { gql } from 'apollo-server-core';
import { packageArchiveSchema } from './archive/package-archive';
import { packageBranchSchema } from './archive/package-branch';
import { packageLocationSchema } from './archive/package-location';
import { packageRevisionSchema } from './archive/package-revision';
import { packageTargetSchema } from './archive/package-target';
import { authSchema } from './auth';
import { contestSchema } from './contest';
import { contestViewSchema } from './contest-view';
import { dateTimeSchema } from './data/date-time';
import { fieldSchema } from './data/field';
import { fileSchema } from './data/file';
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
import { fileContentSchema } from './files/file-content';
import { mainViewSchema } from './main-view';
import { messageSchema } from './message';
import { mutationSchema } from './mutation';
import { objectiveSchema } from './objective-definition';
import { objectiveInstanceSchema } from './objective-instance';
import { objectiveViewSchema } from './objective-view';
import { outcomeSchema } from './outcome';
import { problemSchema } from './problem-definition';
import { submissionFileTypeSchema } from './problem-definition-file-types';
import { problemMaterialSchema } from './problem-definition-material';
import { problemInstanceSchema } from './problem-instance';
import { problemSetSchema } from './problem-set-definition';
import { problemSetUndertakingSchema } from './problem-set-undertaking';
import { problemSetViewSchema } from './problem-set-view';
import { problemUndertakingSchema } from './problem-undertaking';
import { problemViewSchema } from './problem-view';
import { querySchema } from './query';
import { submissionSchema } from './submission';
import { submissionFileSchema } from './submission-file';
import { userSchema } from './user';

/** Full GraphQL schema document. Obtained combining schema parts from each components. */
export const schema = gql`
    ${authSchema}
    ${contestSchema}
    ${contestViewSchema}
    ${dateTimeSchema}
    ${evaluationSchema}
    ${fieldSchema}
    ${fileContentSchema}
    ${fileSchema}
    ${fulfillmentSchema}
    ${gradeSchema}
    ${headerSchema}
    ${mainViewSchema}
    ${mediaSchema}
    ${memoryUsageSchema}
    ${messageFieldSchema}
    ${messageSchema}
    ${mutationSchema}
    ${objectiveInstanceSchema}
    ${objectiveSchema}
    ${objectiveViewSchema}
    ${outcomeSchema}
    ${packageTargetSchema}
    ${packageLocationSchema}
    ${packageRevisionSchema}
    ${packageArchiveSchema}
    ${packageBranchSchema}
    ${problemInstanceSchema}
    ${problemMaterialSchema}
    ${problemSchema}
    ${problemSetSchema}
    ${problemSetUndertakingSchema}
    ${problemSetViewSchema}
    ${problemUndertakingSchema}
    ${problemViewSchema}
    ${querySchema}
    ${scoreSchema}
    ${submissionFileSchema}
    ${submissionFileTypeSchema}
    ${submissionSchema}
    ${textSchema}
    ${timeUsageSchema}
    ${userSchema}
    ${valenceSchema}

    enum Ok {
        OK
    }
`;
