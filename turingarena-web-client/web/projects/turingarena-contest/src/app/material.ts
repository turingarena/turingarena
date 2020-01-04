import gql from 'graphql-tag';

import { MaterialFragment } from './__generated__/MaterialFragment';
import { fileFragment } from './file';
import { rusageFragment } from './rusage';
import { scoreRangeFragment } from './score';
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
    cols { ...ColFragment }
    rows { ...RowFragment }
  }

  fragment ColFragment on Col {
    title { ...TextFragment }
    content { ...ColContentFragment }
  }

  fragment ColContentFragment on ColContent {
    __typename
    ... on ScoreColContent {
      range { ...ScoreRangeFragment }
    }
  }

  fragment RowFragment on Row {
    cells { ...CellFragment }
  }

  fragment CellFragment on Cell {
    content { ...CellContentFragment }
  }

  fragment CellContentFragment on CellContent {
    __typename
    ... on RowNumberCellContent { ...RowNumberCellContentFragment }
    ... on RowTitleCellContent { ...RowTitleCellContentFragment }
    ... on AwardReferenceCellContent { ...AwardReferenceCellContentFragment }
    ... on ScoreCellContent { ...ScoreCellContentFragment }
    ... on MessageCellContent { ...MessageCellContentFragment }
    ... on TimeUsageCellContent { ...TimeUsageCellContentFragment }
    ... on MemoryUsageCellContent { ...MemoryUsageCellContentFragment }
  }

  fragment RowNumberCellContentFragment on RowNumberCellContent {
    number
  }

  fragment RowTitleCellContentFragment on RowTitleCellContent {
    title { ...TextFragment }
  }

  fragment AwardReferenceCellContentFragment on AwardReferenceCellContent {
    awardName
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
    timeUsageMaxRelevant: maxRelevant { ...TimeUsageFragment }
    timeUsagePrimaryWatermark: primaryWatermark { ...TimeUsageFragment }
    key
    valenceKey
  }

  fragment MemoryUsageCellContentFragment on MemoryUsageCellContent {
    memoryUsageMaxRelevant: maxRelevant { ...MemoryUsageFragment }
    memoryUsagePrimaryWatermark: primaryWatermark { ...MemoryUsageFragment }
    key
    valenceKey
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
  ${rusageFragment}
  ${scoreRangeFragment}
`;
