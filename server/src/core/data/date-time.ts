import { gql } from 'apollo-server-core';
import { DateTime } from 'luxon';
import { ApiOutputValue } from '../../main/graphql-types';
import { unreachable } from '../../util/unreachable';
import { Text } from './text';

export const dateTimeSchema = gql`
    "An instant, i.e., a point in time."
    type DateTime {
        "Instant expressed as a UTC date-time, encoded as RFC 3339 / ISO 8601"
        utc: String!
        """
        Instant expressed as a (qualified) local date-time (i.e., with an UTC offset), encoded as RFC 3339 / ISO 8601.
        No assumption should be made about the time zone and offset, only that it represents the same point in time as the UTC.
        Use this over UTC only to improve human readability for development.
        """
        local: String!

        secondsFromEpochDecimal: Float!
        secondsFromEpochInteger: Int!
        millisFromEpochInteger: Int!

        utcOffsetMinutes: Int!
    }

    type DateTimeField {
        dateTime: DateTime
    }

    "Column containing a date-time."
    type DateTimeColumn implements TitledColumn {
        title: Text!
        fieldIndex: Int!
    }
`;

export class ApiDateTime implements ApiOutputValue<'DateTime'> {
    constructor(readonly inner: DateTime) {}

    utc = this.inner.toUTC().toISO() ?? unreachable(`invalid date-time`);
    local = this.inner.toISO() ?? unreachable(`invalid date-time`);
    millisFromEpochInteger = this.inner.toMillis();
    secondsFromEpochDecimal = this.inner.toSeconds();
    secondsFromEpochInteger = Math.floor(this.inner.toSeconds());
    utcOffsetMinutes = this.inner.offset;

    static fromISO(dateTimeString: string) {
        return new ApiDateTime(DateTime.fromISO(dateTimeString));
    }

    static fromJSDate(jsDate: Date) {
        return new ApiDateTime(DateTime.fromJSDate(jsDate));
    }
}

export class DateTimeField implements ApiOutputValue<'DateTimeField'> {
    __typename = 'DateTimeField' as const;

    constructor(readonly dateTime: ApiDateTime | null) {}
}

export class DateTimeColumn implements ApiOutputValue<'DateTimeColumn'> {
    __typename = 'DateTimeColumn' as const;

    constructor(readonly title: Text, readonly fieldIndex: number) {}
}
