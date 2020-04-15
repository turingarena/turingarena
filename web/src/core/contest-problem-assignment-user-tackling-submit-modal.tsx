import { gql, useMutation } from '@apollo/client';
import { css, cx } from 'emotion';
import React, { useRef, useState } from 'react';
import {
  ContestProblemAssignmentUserTacklingSubmitModalFragment,
  ContestProblemAssignmentUserTacklingSubmitModalSubmissionFieldFragment,
  SubmitMutation,
  SubmitMutationVariables,
} from '../generated/graphql-types';
import { useAsync } from '../util/async-hook';
import { buttonCss, buttonNormalizeCss, buttonPrimaryCss } from '../util/components/button';
import { modalBodyCss, modalFooterCss, modalHeaderCss } from '../util/components/modal';
import { loadFileContent } from '../util/file-load';
import { FragmentProps } from '../util/fragment-props';
import { textFragment } from './text';

export const contestProblemAssignmentUserTacklingSubmitModalFragment = gql`
  fragment ContestProblemAssignmentUserTacklingSubmitModalSubmissionFileType on SubmissionFileType {
    name
    title {
      ...Text
    }
  }

  fragment ContestProblemAssignmentUserTacklingSubmitModalSubmissionField on SubmissionField {
    name
    title {
      ...Text
    }
  }

  fragment ContestProblemAssignmentUserTacklingSubmitModalSubmissionFileTypeRule on SubmissionFileTypeRule {
    fields {
      name
    }
    extensions
    defaultType {
      ...ContestProblemAssignmentUserTacklingSubmitModalSubmissionFileType
    }
    recommendedTypes {
      ...ContestProblemAssignmentUserTacklingSubmitModalSubmissionFileType
    }
    otherTypes {
      ...ContestProblemAssignmentUserTacklingSubmitModalSubmissionFileType
    }
  }

  fragment ContestProblemAssignmentUserTacklingSubmitModal on ContestProblemAssignmentUserTackling {
    assignmentView {
      assignment {
        contest {
          name
        }
        problem {
          name
          title {
            ...Text
          }
          submissionFields {
            ...ContestProblemAssignmentUserTacklingSubmitModalSubmissionField
          }
          submissionFileTypeRules {
            ...ContestProblemAssignmentUserTacklingSubmitModalSubmissionFileTypeRule
          }
        }
      }
    }

    user {
      username
    }
  }

  ${textFragment}
`;

export function ContestProblemAssignmentUserTacklingSubmitModal({
  data,
  onSubmitSuccessful,
}: FragmentProps<ContestProblemAssignmentUserTacklingSubmitModalFragment> & {
  onSubmitSuccessful: () => void;
}) {
  const [submit] = useMutation<SubmitMutation, SubmitMutationVariables>(
    gql`
      mutation Submit($submission: SubmissionInput!) {
        submit(submission: $submission)
      }
    `,
    {
      refetchQueries: ['Main'],
      awaitRefetchQueries: true,
    },
  );

  const [loadFilesAndSubmit, { loading, error }] = useAsync(async (formData: FormData) =>
    submit({
      variables: {
        submission: {
          contestName: data.assignmentView.assignment.contest.name,
          problemName: data.assignmentView.assignment.problem.name,
          username: data.user.username,
          files: await Promise.all(
            data.assignmentView.assignment.problem.submissionFields.map(async field => {
              const file = formData.get(`${field.name}.file`) as File;

              return {
                fieldName: field.name,
                fileTypeName: formData.get(`${field.name}.type`) as string,
                fileName: file.name,
                content: await loadFileContent(file),
              };
            }),
          ),
        },
      },
    }),
  );

  return (
    <form
      onSubmit={e => {
        e.preventDefault();
        loadFilesAndSubmit(new FormData(e.target as HTMLFormElement));
        onSubmitSuccessful();
      }}
      className={css`
        width: 40rem;
      `}
    >
      <div className={modalHeaderCss}>
        <h4>
          Solution of: <strong>{data.assignmentView.assignment.problem.title.variant}</strong>
        </h4>
      </div>
      <div
        className={cx(
          modalBodyCss,
          css`
            max-height: calc(100vh - 260px);
            overflow-y: auto;
          `,
        )}
      >
        {data.assignmentView.assignment.problem.submissionFields.map(f => (
          <FileInput key={f.name} data={data} field={f} />
        ))}
      </div>
      {error !== undefined && <>Error in submission: {error.message}</>}
      <div className={modalFooterCss}>
        <button className={cx(buttonCss, buttonPrimaryCss)} disabled={loading} type="submit">
          Submit
        </button>
      </div>
    </form>
  );
}

function FileInput({
  data,
  field,
}: FragmentProps<ContestProblemAssignmentUserTacklingSubmitModalFragment> & {
  field: ContestProblemAssignmentUserTacklingSubmitModalSubmissionFieldFragment;
}) {
  const fileFieldId = `${field.name}.file`;

  const fileInput = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);

  return (
    <>
      <label
        className={css`
          display: block;
        `}
        htmlFor={fileFieldId}
      >
        {field.title.variant}
      </label>
      <input
        className={css`
          display: none;
        `}
        id={fileFieldId}
        name={fileFieldId}
        ref={fileInput}
        type="file"
        onChange={e => setFile(e.target.files !== null ? e.target.files[0] : null)}
      />
      <button
        className={cx(buttonCss, buttonPrimaryCss)}
        onClick={e => {
          fileInput.current?.click();
          e.preventDefault();
        }}
      >
        Choose file
      </button>
      {file !== null && (
        <dl
          className={css`
            display: flex;
            flex-flow: row wrap;

            & > dt {
              margin-bottom: 0px;
              min-width: 6rem;
            }

            & > dd {
              margin-bottom: 0px;
              margin-left: -6rem;
              padding-left: 8rem;
              flex: 1 1 100%;
            }
          `}
        >
          <dt>Name:</dt>
          <dd>{file.name}</dd>
          <dt>Type:</dt>
          <dd>
            <FileTypeInfo data={data} field={field} file={file} />
          </dd>

          <dt>Size:</dt>
          <dd>{file.size}</dd>
        </dl>
      )}
    </>
  );
}

function FileTypeInfo({
  data,
  field,
  file,
}: FragmentProps<ContestProblemAssignmentUserTacklingSubmitModalFragment> & {
  field: ContestProblemAssignmentUserTacklingSubmitModalSubmissionFieldFragment;
  file: File;
}) {
  const rule = getTypingRule({ data, field, file });

  const [overrideType, setOverrideType] = useState(false);
  const defaultType = overrideType ? null : rule.defaultType;

  const typeInputId = `${field.name}.type`;

  if (defaultType === null) {
    return (
      <select name={typeInputId}>
        {rule.recommendedTypes.map(t => (
          <option key={t.name} value={t.name}>
            {t.title.variant}
          </option>
        ))}
        {rule.otherTypes.map(t => (
          <option key={t.name} value={t.name}>
            {t.title.variant}
          </option>
        ))}
      </select>
    );
  } else {
    return (
      <>
        {defaultType.title.variant}(
        <button
          className={cx(
            buttonNormalizeCss,
            css`
              &:hover {
                text-decoration: underline;
              }
            `,
          )}
          onClick={() => setOverrideType(true)}
        >
          change
        </button>
        )
        <input type="hidden" name={typeInputId} value={defaultType.name} />
      </>
    );
  }
}

function getTypingRule({
  data,
  field,
  file,
}: FragmentProps<ContestProblemAssignmentUserTacklingSubmitModalFragment> & {
  field: ContestProblemAssignmentUserTacklingSubmitModalSubmissionFieldFragment;
  file: File;
}) {
  for (const rule of data.assignmentView.assignment.problem.submissionFileTypeRules) {
    const { fields = null, extensions = null } = rule;
    if (fields !== null && fields.find(f => f.name === field.name) === undefined) continue;
    if (extensions !== null && extensions.find(e => file.name.endsWith(e)) === undefined) continue;

    return rule;
  }
  throw new Error(`No file type rule matches the given field and file. The rules must include a catch-all rule.`);
}
