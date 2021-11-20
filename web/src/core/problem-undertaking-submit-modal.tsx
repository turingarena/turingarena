import { gql, useMutation } from '@apollo/client';
import { css, cx } from 'emotion';
import React, { InputHTMLAttributes, useRef, useState } from 'react';
import { Modal } from 'react-bootstrap';
import {
  ProblemUndertakingSubmitModalFragment,
  ProblemUndertakingSubmitModalSubmissionFieldFragment,
  SubmitMutation,
  SubmitMutationVariables,
} from '../generated/graphql-types';
import { useT } from '../translations/main';
import { useAsync } from '../util/async-hook';
import { buttonCss, buttonNormalizeCss, buttonPrimaryCss } from '../util/components/button';
import { loadFileContent } from '../util/file-load';
import { FragmentProps } from '../util/fragment-props';
import { textFragment } from './data/text';

export const problemUndertakingSubmitModalFragment = gql`
  fragment ProblemUndertakingSubmitModalSubmissionFileType on SubmissionFileType {
    name
    title {
      ...Text
    }
  }

  fragment ProblemUndertakingSubmitModalSubmissionField on SubmissionField {
    name
    title {
      ...Text
    }
  }

  fragment ProblemUndertakingSubmitModalSubmissionFileTypeRule on SubmissionFileTypeRule {
    fields {
      name
    }
    extensions
    defaultType {
      ...ProblemUndertakingSubmitModalSubmissionFileType
    }
    recommendedTypes {
      ...ProblemUndertakingSubmitModalSubmissionFileType
    }
    otherTypes {
      ...ProblemUndertakingSubmitModalSubmissionFileType
    }
  }

  fragment ProblemUndertakingSubmitModal on ProblemUndertaking {
    view {
      instance {
        contest {
          id
        }
        definition {
          name
          title {
            ...Text
          }
          submissionFields {
            ...ProblemUndertakingSubmitModalSubmissionField
          }
          submissionFileTypeRules {
            ...ProblemUndertakingSubmitModalSubmissionFileTypeRule
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

export function ProblemUndertakingSubmitModal({
  data,
  onSubmitSuccessful,
}: FragmentProps<ProblemUndertakingSubmitModalFragment> & {
  onSubmitSuccessful: (submissionId: string) => void;
}) {
  const t = useT();
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
          contestId: data.view.instance.contest.id,
          problemName: data.view.instance.definition.name,
          username: data.user.username,
          files: await Promise.all(
            data.view.instance.definition.submissionFields.map(async field => {
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
    >
      <Modal.Header>
        <h4>
          {t('solutionOf')}: <strong>{data.view.instance.definition.title.variant}</strong>
        </h4>
      </Modal.Header>
      <Modal.Body>
        {data.view.instance.definition.submissionFields.map(f => (
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
}: FragmentProps<ProblemUndertakingSubmitModalFragment> & {
  field: ProblemUndertakingSubmitModalSubmissionFieldFragment;
} & InputHTMLAttributes<HTMLInputElement>) {
  const fileFieldId = `${field.name}.file`;

  const t = useT();
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
}: FragmentProps<ProblemUndertakingSubmitModalFragment> & {
  field: ProblemUndertakingSubmitModalSubmissionFieldFragment;
  file: File;
}) {
  const rule = getTypingRule({ data, field, file });
  const t = useT();
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
}: FragmentProps<ProblemUndertakingSubmitModalFragment> & {
  field: ProblemUndertakingSubmitModalSubmissionFieldFragment;
  file: File;
}) {
  for (const rule of data.view.instance.definition.submissionFileTypeRules) {
    const { fields = null, extensions = null } = rule;
    if (fields !== null && fields.find(f => f.name === field.name) === undefined) continue;
    if (extensions !== null && extensions.find(e => file.name.endsWith(e)) === undefined) continue;

    return rule;
  }
  throw new Error(`No file type rule matches the given field and file. The rules must include a catch-all rule.`);
}
