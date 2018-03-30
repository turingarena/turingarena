import React from 'preact';
import PropTypes from 'prop-types';
import './App.css';


const UploadView = ({ onSubmit, disabled }) => (
  <form disabled={disabled} onSubmit={(e) => { e.preventDefault(); onSubmit(e.target); }}>
    <label htmlFor="git_url">
      Git URL: <input id="git_url" type="text" name="git_url" />
    </label>
    <label htmlFor="problem">
      Problem name: <input id="problem" type="text" name="problem" />
    </label>
    <label htmlFor="source_file">
      Source file: <input id="source_file" type="file" name="source_file" />
    </label>
    <select name="language">
      <option value="c++">C/C++</option>
      <option value="python">Python</option>
      <option value="java">Java</option>
      <option value="javascript">Javascript</option>
    </select>
    <button type="submit" disabled={disabled}>Submit</button>
  </form>
);

UploadView.propTypes = {
  disabled: PropTypes.bool.isRequired,
  onSubmit: PropTypes.func.isRequired,
};

const submit = form => fetch(process.env.TURINGARENA_EVALUATE_ENDPOINT, {
  method: 'post',
  body: new FormData(form),
}).then((response) => {
  const text = response.text();
  if (response.status !== 200) {
    return text.then(t => Promise.reject(t));
  }
  return Promise.resolve(text);
});

const ResultView = ({ result }) => (
  <pre>
    {result.evaluation}
  </pre>
);

ResultView.propTypes = {
  result: PropTypes.shape({ evaluation: PropTypes.string.isRequired }).isRequired,
};

class SubmitView extends React.Component {
  state = {
    phase: 'pristine',
    result: {},
  };

  submit(t) {
    this.setState({ phase: 'submitted', result: {} });
    submit(t).then((r) => {
      this.setState({ phase: 'resolved', result: { evaluation: r } });
    }, (r) => {
      this.setState({ phase: 'rejected', result: { error: r } });
    });
  }

  render() {
    return (
      <React.Fragment>
        <UploadView disabled={this.state.phase === 'submitted'} onSubmit={t => this.submit(t)} />
        {this.state.phase === 'submitted' && <p>Evaluating... (may take up to one minute)</p>}
        {this.state.phase === 'resolved' && <ResultView result={this.state.result} />}
        {this.state.phase === 'rejected' && <pre className="ta-error">{this.state.result.error}</pre>}
      </React.Fragment>
    );
  }
}

export default () => (
  <div>
    <SubmitView />
  </div>
);
