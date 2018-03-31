import React from 'react';
import PropTypes from 'prop-types';
import ProblemView from './ProblemView';
import './App.css';

const UploadView = ({ onSubmit, disabled }) => (
  <form disabled={disabled} onSubmit={(e) => { e.preventDefault(); onSubmit(e.target); }}>
    <label className="ta-form-control" htmlFor="git_url">
      Git URL (optional): <input id="git_url" type="text" name="git_url" />
    </label>
    <label className="ta-form-control" htmlFor="problem">
      Problem name: <input id="problem" type="text" name="problem" />
    </label>
    <label className="ta-form-control" htmlFor="source_file">
      Source file: <input id="source_file" type="file" name="source_file" />
    </label>
    <select className="ta-form-control" name="language">
      <option value="c++">C/C++</option>
      <option value="python">Python</option>
      <option value="java">Java</option>
      <option value="javascript">Javascript</option>
    </select>
    <button className="ta-form-control" type="submit" disabled={disabled}>Submit</button>
  </form>
);

UploadView.propTypes = {
  disabled: PropTypes.bool.isRequired,
  onSubmit: PropTypes.func.isRequired,
};

const submit = form => fetch(process.env.TURINGARENA_EVALUATE_ENDPOINT, {
  method: 'post',
  body: new FormData(form),
}).then(response => response.json()).then((response) => {
  if (response.error) {
    return Promise.reject(response.error);
  }
  return response;
});

const GoalsView = ({ goals }) => (
  <React.Fragment>
    {Object.entries(goals).map(([name, result]) => (
      <p key={name}>
        {name}: {
          result
            ? <span style={{ color: 'darkgreen' }}>Success!</span>
            : <span style={{ color: 'darkred' }}>Failed.</span>
        }
      </p>
    ))}
  </React.Fragment>
);

GoalsView.propTypes = { goals: PropTypes.objectOf(PropTypes.any).isRequired };

const ResultView = ({ result }) => (
  <React.Fragment>
    {
      result.evaluation.data
      && result.evaluation.data.goals
      && <GoalsView goals={result.evaluation.data.goals} />
    }
    <pre>
      {result.evaluation.stdout.join('\n')}
    </pre>
  </React.Fragment>
);

ResultView.propTypes = {
  result: PropTypes.shape({ evaluation: PropTypes.any.isRequired }).isRequired,
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
        {this.state.phase === 'rejected' && <pre className="ta-error">{this.state.result.error.message}</pre>}
      </React.Fragment>
    );
  }
}

export default () => (
  <div>
    {process.env.TURINGARENA_PROBLEM_URL && <ProblemView />}
    <SubmitView />
  </div>
);
