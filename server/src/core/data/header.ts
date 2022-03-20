import { gql } from 'apollo-server-core';
import { ApiOutputValue } from '../../main/graphql-types';
import { Text } from './text';

export const headerSchema = gql`
    "Field serving as header (e.g., for a row) containing a title and optionally a numeric index (e.g., for sorting)."
    type HeaderField {
        title: Text!
        index: Int
    }

    "Column containing headers for each row."
    type HeaderColumn implements TitledColumn {
        title: Text!
        fieldIndex: Int!
    }
`;

export class HeaderField implements ApiOutputValue<'HeaderField'> {
    __typename = 'HeaderField' as const;

    constructor(readonly title: Text, readonly index: number | null) {}
}

export class HeaderColumn implements ApiOutputValue<'HeaderColumn'> {
    __typename = 'HeaderColumn' as const;

    constructor(readonly title: Text, readonly fieldIndex: number) {}
}
