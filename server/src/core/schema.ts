import { gql } from 'apollo-server-core';
import { achievementSchema } from './achievement';
import { authSchema } from './auth';
import { contestSchema } from './contest';
import { contestObjectiveAssignmentSchema } from './contest-objective-assignment';
import { contestProblemAssignmentSchema } from './contest-problem-assignment';
import { contestProblemAssignmentUserTacklingSchema } from './contest-problem-assignment-user-tackling';
import { contestProblemSetSchema } from './contest-problem-set';
import { contestProblemSetUserTacklingSchema } from './contest-problem-set-user-tackling';
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
import { contestObjectiveAssignmentViewSchema } from './view/contest-objective-assignment-view';
import { contestProblemAssignmentViewSchema } from './view/contest-problem-assignment-view';
import { contestProblemSetViewSchema } from './view/contest-problem-set-view';
import { contestViewSchema } from './view/contest-view';
import { mainViewSchema } from './view/main-view';

/** Full GraphQL schema document. Obtained combining schema parts from each components. */
export const schema = gql`
    ${achievementSchema}
    ${archiveSchema}
    ${authSchema}
    ${objectiveSchema}
    ${contestObjectiveAssignmentSchema}
    ${contestObjectiveAssignmentViewSchema}
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
