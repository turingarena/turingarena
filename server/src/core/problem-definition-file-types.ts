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
    constructor(readonly name: string, readonly extension: string, readonly title: Text) {}
}

export interface SubmissionFileTypeRule extends ApiOutputValue<'SubmissionFileTypeRule'> {
    extensions: string[];
    defaultType: SubmissionFileType;
    recommendedTypes: SubmissionFileType[];
    otherTypes: SubmissionFileType[];
    fields: null; // TODO
}

const lang = {
    python2: new SubmissionFileType('python2', '.py', new Text([{ value: 'Python 2 (cpython)' }])),
    python3: new SubmissionFileType('py', '.py', new Text([{ value: 'Python 3 (cpython)' }])),
    c: new SubmissionFileType('c', '.c', new Text([{ value: 'C (c11)' }])),
    cpp: new SubmissionFileType('cpp', '.cpp', new Text([{ value: 'C++ (c++17)' }])),
    rust: new SubmissionFileType('rust', '.rust', new Text([{ value: 'Rust' }])),
    java: new SubmissionFileType('java', '.java', new Text([{ value: 'Java 8 (JDK)' }])),
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
