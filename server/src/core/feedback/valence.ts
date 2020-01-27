import { gql } from 'apollo-server-core';

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
        E.g., a award is given full score.
        """
        SUCCESS
        """
        A partial success.
        E.g., a award is given partial score.
        """
        PARTIAL
        """
        A failed result.
        E.g., time limit exceeded causes the loss of an award.
        """
        FAILURE
        """
        The user should pay attention to something because it could result in a future failure.
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
        E.g., the compilation of a source program written in Python is note performed.
        """
        IGNORED
        """
        An operation is not performed, because a previous _failure_ makes it unnecessary.
        E.g., a large test case is not evaluated because a solution fails in a smaller one.
        """
        BLOCKED
    }

    "Object containing a qualitative feeling (valence)."
    type ValenceValue {
        "The qualitative feeling."
        valence: Boolean!
        "Dummy object representing the domain of this value."
        domain: ValenceDomain!
    }

    "Dummy type representing the possible values for a valence"
    type ValenceDomain {
        _: Boolean
    }

    "Variable containing a valence"
    type ValenceVariable {
        domain: ValenceDomain!
        value: ValenceValue
    }
`;
