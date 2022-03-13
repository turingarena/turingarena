import { gql } from 'apollo-server-core';
import { ApiOutputValue } from '../main/graphql-types';
import { Text } from './data/text';

export const submissionFileTypeSchema = gql`
    type SubmissionFileType {
        name: String!
        title: Text!
    }

    type SubmissionFileTypeRule {
        """
        Set of fields matched by this rule.
        If null, matches all fields.
        """
        fields: [SubmissionField!]
        """
        Set of file extensions matched by this rule, including the initial dot.
        If null, matches any extension.
        """
        extensions: [String!]

        "Type tu use as default, if not null."
        defaultType: SubmissionFileType
        "List of recommended types the user can choose from. Should include the default type first, if any."
        recommendedTypes: [SubmissionFileType!]!
        "List of other types the user can choose from."
        otherTypes: [SubmissionFileType!]!
    }
`;

export class SubmissionFileType implements ApiOutputValue<'SubmissionFileType'> {
    constructor(readonly name: string, readonly title: Text) {}
}

export type SubmissionFileTypeRule = ApiOutputValue<'SubmissionFileTypeRule'>;

const lang = {
    python2: new SubmissionFileType('python2', new Text([{ value: 'Python 2 (cpython)' }])),
    python3: new SubmissionFileType('py', new Text([{ value: 'Python 3 (cpython)' }])),
    c: new SubmissionFileType('c', new Text([{ value: 'C (c11)' }])),
    cpp: new SubmissionFileType('cpp', new Text([{ value: 'C++ (c++17)' }])),
    rust: new SubmissionFileType('rust', new Text([{ value: 'Rust' }])),
    java: new SubmissionFileType('java', new Text([{ value: 'Java 8 (JDK)' }])),
};

export const submissionFileTypes: SubmissionFileType[] = Object.values(lang);

export const submissionFileTypeRules: SubmissionFileTypeRule[] = [
    {
        extensions: ['.c', '.h'],
        defaultType: lang.c,
        recommendedTypes: [lang.c],
        otherTypes: [lang.cpp],
        fields: null,
    },
    {
        extensions: ['.py'],
        defaultType: lang.python3,
        recommendedTypes: [lang.python3, lang.python2],
        otherTypes: [],
        fields: null,
    },
    {
        extensions: ['.cpp', '.hpp', '.cc', '.cxx'],
        defaultType: lang.cpp,
        recommendedTypes: [lang.cpp],
        otherTypes: [],
        fields: null,
    },
    {
        extensions: ['.java'],
        defaultType: lang.java,
        recommendedTypes: [lang.java],
        otherTypes: [],
        fields: null,
    },
    {
        extensions: ['.rs'],
        defaultType: lang.rust,
        recommendedTypes: [lang.rust],
        otherTypes: [],
        fields: null,
    },
];
