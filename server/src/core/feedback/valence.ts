import { gql } from 'apollo-server-core';
import { ApiGraphQLValue } from '../../main/graphql-types';

export const valenceSchema = gql`
    """
    Qualitative feeling associated to something.

    These enum variants are meant to be used only to control the appearance of feedback items.
    They might not all be applicable in every context, and their precise interpretation may depend on the context.
    They are all intentionally gathered together for simplicity.
    """
    enum Valence {
        """
        A successful result.
        E.g., an award is given full score.
        """
        SUCCESS
        """
        A partial success.
        E.g., an award is given partial score.
        """
        PARTIAL
        """
        A failed result.
        E.g., time limit exceeded causes the loss of an award.
        """
        FAILURE
        """
        The user should pay attention to something because it could result in a failure.
        E.g., memory usage approaches the limit.
        """
        WARNING
        """
        An operation is completed successfully, as usually expected.
        E.g., a submitted source compiles correctly.
        """
        NOMINAL
        """
        An operation is not performed, because a previous _success_ makes it unnecessary.
        E.g., an award is not evaluated because already achieved.
        """
        SKIPPED
        """
        An operation is not performed, because irrelevant in the context.
        E.g., the compilation of a source program written in Python is not performed.
        """
        IGNORED
        """
        An operation is not performed, because a previous _failure_ makes it unnecessary.
        E.g., a large test case is not evaluated because a solution fails in a smaller one.
        """
        BLOCKED
    }

    interface HasValence {
        valence: Valence
    }
`;

export type Valence = ApiGraphQLValue<'Valence'>;
