import { gql } from '@apollo/client';
import { IconProp } from '@fortawesome/fontawesome-svg-core';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { css, cx } from 'emotion';
import React, { HTMLAttributes } from 'react';
import { ProblemViewAsideFragment } from '../generated/graphql-types';
import { useT } from '../translations/main';
import { badgeCss, getBadgeCssByValence } from '../util/components/badge';
import { FragmentProps } from '../util/fragment-props';
import { ProblemTacklingAside, problemTacklingAsideFragment } from './contest-problem-assignment-user-tackling-aside';
import { Field, fieldFragment } from './fields/field';
import { GradeField, gradeFieldFragment, scoreFieldFragment } from './fields/grade-field';
import { MediaDownload, mediaDownloadFragment } from './media-download';
import { mediaInlineFragment } from './media-inline';
import { textFragment } from './text';

export const problemViewAsideFragment = gql`
  fragment ProblemViewAside on ProblemView {
    instance {
      id
      definition {
        id
        name
        title {
          ...Text
        }
        statement {
          ...MediaInline
          ...MediaDownload
        }
        attributes {
          title {
            ...Text
          }
          field {
            ...Field
          }
          icon
        }
        attachments {
          title {
            ...Text
          }
          media {
            ...MediaDownload
          }
        }
      }
    }

    totalScoreField {
      ...ScoreField
    }

    objectives {
      instance {
        id
        definition {
          id
          name
          title {
            ...Text
          }
        }
      }

      gradeField {
        ...GradeField
      }
    }

    tackling {
      ...ProblemTacklingAside
    }
  }

  ${textFragment}
  ${mediaInlineFragment}
  ${mediaDownloadFragment}
  ${fieldFragment}
  ${scoreFieldFragment}
  ${gradeFieldFragment}
  ${problemTacklingAsideFragment}
`;

const asideTitleCss = css`
  text-transform: uppercase;
  font-size: 1.125rem;
  margin: 0 0 0.5rem;
  font-weight: 500;
  line-height: 1.2;
`;

const downloadLinkCss = css`
  display: block;
  color: inherit;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;

  &:hover {
    text-decoration: none;
  }
`;

export function ProblemViewAside({
  data,
  className,
  ...rest
}: FragmentProps<ProblemViewAsideFragment> & HTMLAttributes<HTMLDivElement>) {
  const t = useT();

  return (
    <div
      className={cx(
        className,
        css`
          flex: 0 0 auto;
          width: 15em;
          background-color: #f8f9fa;
        `,
      )}
      {...rest}
    >
      {data.tackling !== null && <ProblemTacklingAside data={data.tackling} />}
      <div
        className={css`
          padding: 16px;
          flex: 1 1 100%;
          overflow-y: auto;
        `}
      >
        {data.objectives.length > 0 && (
          <>
            <h3 className={asideTitleCss}>{t('objectives')}</h3>
            <div
              className={css`
                padding: 0;
                list-style: none;

                margin-bottom: 16px;
              `}
            >
              {data.objectives.map(v => (
                <div
                  key={v.instance.id}
                  className={css`
                    height: 32px;
                    border-radius: 16px;
                    padding: 0 8px;
                    cursor: pointer;

                    background-color: rgba(0, 0, 0, 0.03);
                    background-clip: padding-box;
                    border: 1px solid rgba(0, 0, 0, 0.1);

                    &:hover {
                      background-color: rgba(0, 0, 0, 0.01);
                    }

                    display: flex;
                    flex-direction: row;
                    align-items: center;

                    &:not(:first-of-type) {
                      margin-top: 8px;
                    }
                  `}
                  title={v.instance.definition.title.variant}
                >
                  <span
                    className={css`
                      overflow: hidden;
                      text-overflow: ellipsis;
                      white-space: nowrap;
                      flex: 1 1 auto;
                    `}
                  >
                    {v.instance.definition.title.variant}
                  </span>
                  <span className={cx(badgeCss, getBadgeCssByValence(v.gradeField?.valence ?? null))}>
                    <GradeField data={v.gradeField} />
                  </span>
                </div>
              ))}
            </div>
          </>
        )}
        <h3 className={asideTitleCss}>{t('info')}</h3>
        {data.instance.definition.attributes.length > 0 && (
          <>
            <div
              className={css`
                margin-bottom: 16px;
              `}
            >
              {data.instance.definition.attributes.map(a => (
                <div
                  key={a.title.variant}
                  className={css`
                    margin: 0 -16px;
                    padding: 0 16px;

                    overflow: hidden;

                    display: flex;
                    flex-direction: row;

                    align-items: baseline;
                  `}
                  title={a.title.variant}
                >
                  {a.icon !== null && (
                    <FontAwesomeIcon
                      icon={a.icon as IconProp}
                      className={css`
                        margin-right: 5px;
                        min-width: 20px;
                        text-align: 'left';
                      `}
                    />
                  )}
                  <span
                    className={css`
                      overflow: hidden;
                      text-overflow: ellipsis;
                      white-space: nowrap;
                    `}
                  >
                    {a.title.variant}
                  </span>
                  <span
                    className={css`
                      margin-left: auto;
                      font-weight: bold;
                      font-size: 90%;
                    `}
                  >
                    <Field data={a.field} />
                  </span>
                </div>
              ))}
            </div>
          </>
        )}
        <MediaDownload
          className={cx(
            downloadLinkCss,
            css`
              margin-bottom: 16px;
            `,
          )}
          data={data.instance.definition.statement}
          text={t('downloadStatement')}
        />
        {data.instance.definition.attachments.length > 0 && (
          <>
            <h3 className={asideTitleCss}>{t('attachments')}</h3>
            <div
              className={css`
                margin-bottom: 16px;
              `}
            >
              {data.instance.definition.attachments.map((a, i) => (
                <MediaDownload
                  key={a.title.variant}
                  className={downloadLinkCss}
                  data={a.media}
                  text={a.title.variant}
                />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
