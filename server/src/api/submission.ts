import { gql } from 'apollo-server-core';

export const submissionSchema = gql`
    type Submission {
        id: ID!
        problem: Problem!
        user: User!
        contest: Contest!
        files: [SubmissionFile!]!
        createdAt: String!
        officialEvaluation: Evaluation!
        evaluations: [Evaluation!]!
    }

    type SubmissionFile {
        fieldId: ID!
        file: File!
    }

    input SubmissionInput {
        problemName: ID!
        contestName: ID!
        username: ID!
        files: [SubmissionFileInput!]!
    }

    input SubmissionFileInput {
        fieldId: ID!
        file: FileInput!
    }

    type Evaluation {
        submission: Submission!
        events: [EvaluationEvent!]!
    }

    type EvaluationEvent {
        evaluation: Evaluation!
        data: String!
    }
`;
