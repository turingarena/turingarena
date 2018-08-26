import React from 'react';

const ElementView = ({ data }) => (
  data.element_type ? (
    <data.element_type {...data.attributes}>
      <DocumentView data={data.children} />
    </data.element_type>
  ) : data
);
ElementView.propTypes = {
  data: ElementType.isRequired,
};

const DocumentView = ({ data }) => (
  data.map(e => <ElementView data={e} />)
);
DocumentView.propTypes = {
  data: DocumentType.isRequired,
};
