import gql from 'graphql-tag';

import { MaterialFragment } from './__generated__/MaterialFragment';
import { fileFragment } from './file';
import { textFragment } from './text';

export const problemMaterialFragment = gql`
  fragment AttachmentFragment on Attachment {
    title { ...TextFragment }
    file { ...FileFragment }
  }

  fragment FieldTypeFragment on FileType {
    id
    title { ...TextFragment }
    extensions
  }

  fragment FieldFragment on Field {
    id
    title { ...TextFragment }
    types { ...FieldTypeFragment }
  }

  fragment FormFragment on Form {
    fields { ...FieldFragment }
  }

  fragment AwardFragment on Award {
    name
    title { ...TextFragment }
    content {
      __typename
      ... on ScoreAwardContent {
        range {
          ...ScoreRangeFragment
        }
      }
    }
  }

  fragment TableSectionFragment on TableSection {
    caption { ...TextFragment }
    cols {
      title { ...TextFragment }
      content {
        __typename
        ... on ScoreColContent {
          range { ...ScoreRangeFragment }
        }
      }
    }
    rowGroups { ...RowGroupFragment }
  }

  fragment RowNumberCellContentFragment on RowNumberCellContent {
    number
  }

  fragment RowTitleCellContentFragment on RowTitleCellContent {
    title { ...TextFragment }
  }

  fragment ScoreCellContentFragment on ScoreCellContent {
    key
    range { ...ScoreRangeFragment }
  }

  fragment MessageCellContentFragment on MessageCellContent {
    key
    valenceKey
  }

  fragment TimeUsageCellContentFragment on TimeUsageCellContent {
    timeUsageMaxRelevant: maxRelevant
    timeUsagePrimaryWatermark: primaryWatermark
    key
    valenceKey
  }

  fragment MemoryUsageCellContentFragment on MemoryUsageCellContent {
    memoryUsageMaxRelevant: maxRelevant
    memoryUsagePrimaryWatermark: primaryWatermark
    key
    valenceKey
  }

  fragment ScoreRangeFragment on ScoreRange {
    max
    precision
  }

  fragment RowGroupFragment on RowGroup {
    title { ...TextFragment }
    rows {
      content
      cells {
        content {
          __typename
          ... on RowNumberCellContent { ...RowNumberCellContentFragment }
          ... on RowTitleCellContent { ...RowTitleCellContentFragment }
          ... on ScoreCellContent { ...ScoreCellContentFragment }
          ... on MessageCellContent { ...MessageCellContentFragment }
          ... on TimeUsageCellContent { ...TimeUsageCellContentFragment }
          ... on MemoryUsageCellContent { ...MemoryUsageCellContentFragment }
        }
      }
    }
  }

  fragment FeedbackSectionFragment on Section {
    __typename
    ... on TableSection { ...TableSectionFragment }
  }

  fragment MaterialFragment on Material {
    title { ...TextFragment }
    statement { ...FileFragment }
    attachments { ...AttachmentFragment }
    submissionForm { ...FormFragment }
    awards { ...AwardFragment }
    feedback { ...FeedbackSectionFragment }
  }

  ${textFragment}
  ${fileFragment}
`;

export const getAwardScoreRanges = (material: MaterialFragment) => material.awards.map(({ name, content }) => {
  if (content.__typename === 'ScoreAwardContent') {
    return { name, range: content.range };
  } else {
    return { name, range: { precision: 0, max: 0 } };
  }
});

export const getProblemScoreRange = (material: MaterialFragment) => ({
  max: getAwardScoreRanges(material).map(({ range: { max } }) => max).reduce((a: number, b: number) => a + b, 0),
  precision: getAwardScoreRanges(material).map(({ range: { precision } }) => precision).reduce((a, b) => Math.max(a, b)),
});

