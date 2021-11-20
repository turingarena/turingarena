import { gql, useMutation, useQuery } from '@apollo/client';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import React, { useState } from 'react';
import { Button, Modal } from 'react-bootstrap';
import { defineMessage, FormattedMessage, useIntl } from 'react-intl';
import {
  MessagesQuery,
  MessagesQueryVariables,
  SendMessageMutation,
  SendMessageMutationVariables,
} from '../generated/graphql-types';
import { useAuth } from '../util/auth';
import { Message, messageFragment } from './message';

const messagesQuery = gql`
  query Messages($id: ID!) {
    messages(id: $id) {
      ...Message
    }
  }

  ${messageFragment}
`;

const sendMessageMutation = gql`
  mutation SendMessage($message: MessageInput!) {
    sendMessage(message: $message) {
      ...Message
    }
  }

  ${messageFragment}
`;

export function MessagesModal({ onClose }: { onClose: () => void }) {
  const { auth } = useAuth();
  const userId = auth!.currentAuth!.username;
  const [messageText, setMessageText] = useState('');
  const { data, loading, error, refetch } = useQuery<MessagesQuery, MessagesQueryVariables>(messagesQuery, {
    variables: { id: userId },
  });
  const [sendMessage, { loading: sending }] = useMutation<SendMessageMutation, SendMessageMutationVariables>(
    sendMessageMutation,
  );

  const onSendMessage = async () => {
    await sendMessage({
      variables: {
        message: {
          to: null,
          from: userId,
          title: null,
          parent: null,
          content: messageText,
          meta: [],
        },
      },
    });

    setMessageText('');

    // TODO: this is not good
    await refetch();
  };

  const intl = useIntl();

  return (
    <>
      <Modal.Header>
        <FormattedMessage id="messages-header" defaultMessage="Messages" />
      </Modal.Header>
      <Modal.Body>
        {loading && (
          <h1>
            <FormattedMessage id="messages-loading-message" defaultMessage="Loading..." />
          </h1>
        )}
        {data !== undefined &&
          data.messages.map((message, index) => (
            <div key={index}>
              <Message data={message} />
              <hr />
            </div>
          ))}
        <div>
          <textarea
            className="form-control"
            value={messageText}
            placeholder={intl.formatMessage(
              defineMessage({
                id: 'messages-new-message-text-placeholder',
                defaultMessage: `Write your message...`,
              }),
            )}
            onChange={e => setMessageText(e.target.value)}
          />
        </div>
      </Modal.Body>
      <Modal.Footer>
        <Button onClick={onClose} variant="secondary">
          <FormattedMessage id="messages-close-button-label" defaultMessage="Close" />
        </Button>
        <Button disabled={messageText.length <= 0 || sending} variant="primary" onClick={onSendMessage}>
          <FontAwesomeIcon icon="paper-plane" />{' '}
          <FormattedMessage id="messages-new-message-send-button-label" defaultMessage="Send" />
        </Button>
      </Modal.Footer>
    </>
  );
}
