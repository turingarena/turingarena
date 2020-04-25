import { gql, useQuery, useMutation } from '@apollo/client';
import React, { useState } from 'react';
import { Button, Modal } from 'react-bootstrap';
import {
  MessagesQuery,
  MessagesQueryVariables,
  SendMessageMutation,
  SendMessageMutationVariables,
} from '../generated/graphql-types';
import { useT } from '../translations/main';
import { Message, messageFragment } from './message';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { useAuth } from '../util/auth';

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
  const t = useT();
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

  return (
    <>
      <Modal.Header>{t('messages')}</Modal.Header>
      <Modal.Body>
        {loading && <h1>Loading</h1>}
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
            placeholder="write your message"
            onChange={e => setMessageText(e.target.value)}
          />
        </div>
      </Modal.Body>
      <Modal.Footer>
        <Button onClick={onClose} variant="secondary">
          {t('close')}
        </Button>
        <Button disabled={messageText.length <= 0 || sending} variant="primary" onClick={onSendMessage}>
          <FontAwesomeIcon icon="paper-plane" /> {t('send')}
        </Button>
      </Modal.Footer>
    </>
  );
}
