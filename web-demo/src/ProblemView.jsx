import React from 'react';
import PropTypes from 'prop-types';

const ElementType = PropTypes.oneOfType([PropTypes.string, PropTypes.shape({
  element_type: PropTypes.string.isRequired,
  attributes: PropTypes.shape({}),
  children: PropTypes.array,
})]);
const DocumentType = PropTypes.arrayOf(ElementType);
const InterfaceType = PropTypes.shape({});

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

const InterfaceView = ({ data }) => (
  <React.Fragment>
    <React.Fragment>
      {Object.entries(data.global_variables).map(([name]) => (
        <p key={name}>Global variable: <code>{name}</code></p>
      ))}
    </React.Fragment>
    <React.Fragment>
      {Object.entries(data.functions).map(([name]) => (
        <p key={name}>Function: <code>{name}</code></p>
      ))}
    </React.Fragment>
    <React.Fragment>
      {Object.entries(data.callbacks).map(([name]) => (
        <p key={name}>Callback: <code>{name}</code></p>
      ))}
    </React.Fragment>
  </React.Fragment>
);
InterfaceView.propTypes = {
  data: InterfaceType.isRequired,
};

const ProblemDataView = ({ data }) => (
  <React.Fragment>
    {data.interface && <InterfaceView data={data.interface} />}
    {data.doc && <DocumentView data={data.doc} />}
  </React.Fragment>
);
ProblemDataView.propTypes = {
  data: PropTypes.shape({ interface: InterfaceType, doc: DocumentType }).isRequired,
};

export default class ProblemView extends React.Component {
  state = {
    phase: 'pristine',
    data: null,
    error: null,
  };

  componentDidMount() {
    this.load();
  }

  load() {
    this.setState({ phase: 'loading' });
    fetch(process.env.TURINGARENA_PROBLEM_URL).then(r => r.json()).then((r) => {
      this.setState({ phase: 'resolved', data: r });
    }, (r) => {
      this.setState({ phase: 'rejected', error: r });
    });
  }

  render() {
    return (
      <React.Fragment>
        {this.state.phase === 'loading' && <p>Loading...</p>}
        {this.state.phase === 'resolved' && <ProblemDataView data={this.state.data} />}
        {this.state.phase === 'rejected' && <pre className="ta-error">{this.state.error.message}</pre>}
      </React.Fragment>
    );
  }
}
