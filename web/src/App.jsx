import React from 'preact';
import PropTypes from 'prop-types';
import './App.css';


const UploadView = ({ onSubmit, disabled }) => (
  <form disabled={disabled} onSubmit={(e) => { e.preventDefault(); onSubmit(e.target); }}>
    <select name="problem">
      <option>turingarena.problems.sum_of_two_numbers</option>
      <option>turingarena.problems.max_in_sequence</option>
      <option>turingarena.problems.triangle_dynamic_programming</option>
    </select>
    <input type="file" name="source_file" />
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
  if (response.status !== 200) {
    return Promise.reject(response);
  }
  return response.text();
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
        {this.state.phase === 'rejected' && <pre>{this.state.result.error}</pre>}
      </React.Fragment>
    );
  }
}

export default () => (
  <div>
    <SubmitView />
  </div>
);
