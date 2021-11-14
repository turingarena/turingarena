import { gql } from 'apollo-server-core';
import { Op } from 'sequelize';
import { AllowNull, Column, DataType, Table } from 'sequelize-typescript';
import { ApiObject } from '../main/api';
import { UuidBaseModel } from '../main/base-model';
import { ApiOutputValue } from '../main/graphql-types';

export const messageSchema = gql`
    type Message {
        id: ID!
        from: ID
        to: ID
        parent: ID
        title: String
        content: String!
        meta: [MessageMeta!]!
    }

    type MessageMeta {
        key: String!
        value: String!
    }

    input MessageInput {
        from: ID
        to: ID
        parent: ID
        title: String
        content: String!
        meta: [MessageMetaInput!]!
    }

    input MessageMetaInput {
        key: String!
        value: String!
    }
`;

type MessageInput = ApiOutputValue<'MessageInput'>;

@Table({ tableName: 'message' })
export class Message extends UuidBaseModel<Message> {
    @Column(DataType.UUIDV4)
    from!: string | null;

    @Column(DataType.UUIDV4)
    to!: string | null;

    @Column(DataType.UUIDV4)
    parent!: string | null;

    @Column(DataType.STRING)
    title!: string | null;

    @AllowNull(false)
    @Column(DataType.STRING)
    content!: string;

    @AllowNull(false)
    @Column(DataType.JSON)
    meta!: Array<{
        key: string;
        value: string;
    }>;
}

export class MessageApi extends ApiObject {
    async sendMessage(message: MessageInput) {
        return this.ctx.table(Message).create(message);
    }

    async fromId(id: string) {
        return this.ctx.table(Message).findOne({ where: { id } });
    }

    async find(id: string) {
        return this.ctx.table(Message).findAll({ where: { [Op.or]: [{ id }, { from: id }, { to: id }] } });
    }
}
