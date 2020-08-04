import { gql } from 'apollo-server-core';
import { DateTime } from 'luxon';
import { ResolverFn } from '../../generated/graphql-types';
import { ApiContext } from '../../main/api-context';
import { Resolvers } from '../../main/resolver-types';

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
        secondsFromEpochInteger: Float!
        millisFromEpochInteger: Float!

        utcOffsetMinutes: Int!
    }
`;

type DateModel = Date | DateTime | string;

export interface DateTimeModelRecord {
    DateTime: DateModel;
}

function makeDateTime(dateTime: DateModel, ctx: ApiContext) {
    if (typeof dateTime === 'string') return DateTime.fromISO(dateTime);
    if (dateTime instanceof DateTime) return dateTime;
    if (dateTime instanceof Date) return DateTime.fromJSDate(dateTime);
    ctx.fail(`Invalid date-time: ${dateTime}`);
}

function makeDateTimeResolver<T>(
    resolver: ResolverFn<T, DateTime, ApiContext, {}>,
): ResolverFn<T, DateModel, ApiContext, {}> {
    return (dateTime: DateModel, args, ctx, info) => resolver(makeDateTime(dateTime, ctx), args, ctx, info);
}

export const dateTimeResolvers: Resolvers = {
    DateTime: {
        utc: makeDateTimeResolver(t => t.toUTC().toISO() ?? `invalid date-time`),
        local: makeDateTimeResolver(t => t.toISO() ?? `invalid date-time`),
        millisFromEpochInteger: makeDateTimeResolver(t => t.toMillis()),
        secondsFromEpochDecimal: makeDateTimeResolver(t => t.toSeconds()),
        secondsFromEpochInteger: makeDateTimeResolver(t => Math.floor(t.toSeconds())),
        utcOffsetMinutes: makeDateTimeResolver(t => t.offset),
    },
};
