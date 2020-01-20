import { gql } from 'apollo-server-core';

export const feedbackSlotSchema = gql`
    "Container for a feedback value computed during evaluation"
    type FeedbackSlot {
        name: String!
        domain: FeedbackSlotDomain!
    }

    union FeedbackSlotValue = GradeValue | MessageValue

    union FeedbackSlotDomain = GradeDomain | MessageDomain

    union MessageValue = Text;

    type MessageDomain {
        _: Boolean
    }
`;
