import { gql } from 'apollo-server-core';

export const feedbackSlotSchema = gql`
    "Container for a feedback value computed during evaluation"
    type FeedbackSlot {
        name: String!
        domain: FeedbackSlotDomain!
    }

    union FeedbackSlotValue = NumericGradeValue | BooleanGradeValue | Text

    union FeedbackSlotDomain = NumericGradeDomain | BooleanGradeDomain | MessageDomain

    type MessageValue {
        text: Text!
    }

    type MessageDomain {
        _: Boolean
    }
`;
