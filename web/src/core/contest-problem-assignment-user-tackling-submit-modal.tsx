import { gql, useMutation } from '@apollo/client';
import { css, cx } from 'emotion';
import React, { InputHTMLAttributes, useRef, useState } from 'react';
import { Modal } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';
import {
  ContestProblemAssignmentUserTacklingSubmitModalFragment,
  ContestProblemAssignmentUserTacklingSubmitModalSubmissionFieldFragment,
  SubmitMutation,
  SubmitMutationVariables,
} from '../generated/graphql-types';
import { useAsync } from '../util/async-hook';
import { buttonCss, buttonNormalizeCss, buttonPrimaryCss } from '../util/components/button';
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
          id
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
  onSubmitSuccessful: (submissionId: string) => void;
}) {
  const { t } = useTranslation();
  const [submit] = useMutation<SubmitMutation, SubmitMutationVariables>(
    gql`
      mutation Submit($submission: SubmissionInput!) {
        submit(submission: $submission) {
          id
        }
      }
    `,
    {
      refetchQueries: ['Main'],
      awaitRefetchQueries: true,
    },
  );

  const [loadFilesAndSubmit, { loading, error }] = useAsync(async (formData: FormData) => {
    const submission = await submit({
      variables: {
        submission: {
          contestId: data.assignmentView.assignment.contest.id,
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
    });

    const submissionId = submission.data?.submit.id;
    if (submissionId !== undefined) {
      onSubmitSuccessful(submissionId);
    } else {
      throw new Error(`Cannot get new submission ID.`);
    }
  });

  const [valid, setValid] = useState(false);
  const formRef = useRef<HTMLFormElement | null>(null);

  return (
    <form
      ref={formRef}
      onChange={e => setValid((e.target as HTMLFormElement).checkValidity())}
      onSubmit={e => {
        e.preventDefault();
        loadFilesAndSubmit(new FormData(e.target as HTMLFormElement));
      }}
      className={css`
        width: 40rem;
      `}
    >
      <Modal.Header>
        <h4>
          {t('solutionOf')}: <strong>{data.assignmentView.assignment.problem.title.variant}</strong>
        </h4>
      </Modal.Header>
      <Modal.Body
        className={css`
          max-height: calc(100vh - 260px);
          overflow-y: auto;
        `}
      >
        {data.assignmentView.assignment.problem.submissionFields.map(f => (
          <FileInput
            key={f.name}
            data={data}
            field={f}
            onChange={() => setValid(formRef.current?.checkValidity() ?? false)}
          />
        ))}
        {error !== undefined && (
          <>
            {t('submissionError')}: {error.message}
          </>
        )}
      </Modal.Body>
      <Modal.Footer>
        <button className={cx(buttonCss, buttonPrimaryCss)} disabled={loading || !valid} type="submit">
          {t('submit')}
        </button>
      </Modal.Footer>
    </form>
  );
}

function FileInput({
  data,
  field,
  onChange,
  ...rest
}: FragmentProps<ContestProblemAssignmentUserTacklingSubmitModalFragment> & {
  field: ContestProblemAssignmentUserTacklingSubmitModalSubmissionFieldFragment;
} & InputHTMLAttributes<HTMLInputElement>) {
  const fileFieldId = `${field.name}.file`;

  const { t } = useTranslation();
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
        required
        onChange={e => {
          setFile(e.target.files !== null ? e.target.files[0] ?? null : null);
          if (onChange !== undefined) onChange(e);
        }}
        {...rest}
      />
      <button
        className={cx(buttonCss, buttonPrimaryCss)}
        onClick={e => {
          fileInput.current?.click();
          e.preventDefault();
        }}
      >
        {t('chooseFile')}
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
          <dt>{t('name')}:</dt>
          <dd>{file.name}</dd>
          <dt>{t('type')}:</dt>
          <dd>
            <FileTypeInfo data={data} field={field} file={file} />
          </dd>

          <dt>{t('size')}:</dt>
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
  const { t } = useTranslation();
  const [overrideType, setOverrideType] = useState(false);
  const defaultType = overrideType ? null : rule.defaultType;

  const typeInputId = `${field.name}.type`;

  if (defaultType === null) {
    return (
      <select name={typeInputId}>
        {rule.recommendedTypes.map(type => (
          <option key={t.name} value={type.name}>
            {type.title.variant}
          </option>
        ))}
        {rule.otherTypes.map(type => (
          <option key={t.name} value={type.name}>
            {type.title.variant}
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
          {t('change')}
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
