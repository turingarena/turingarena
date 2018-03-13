import React from 'preact';
import ReactModal from 'react-modal';
import PropTypes from 'prop-types';
import './App.css';


const UploadView = ({ onSubmit }) => (
  <form onSubmit={(e) => { e.preventDefault(); onSubmit(e.target); }}>
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
    <button type="submit">Submit</button>
  </form>
);

UploadView.propTypes = {
  onSubmit: PropTypes.func.isRequired,
};

const submit = (form) => {
  console.log(process.env.TURINGARENA_EVALUATE_ENDPOINT);
  return fetch(process.env.TURINGARENA_EVALUATE_ENDPOINT, {
    method: 'post',
    body: new FormData(form),
  }).then((response) => {
    if (response.status !== 200) {
      return Promise.reject(response);
    }
    return response.text();
  });
};

class SubmitView extends React.Component {
  state = {
    result: null,
  };

  render() {
    return (
      <React.Fragment>
        <UploadView onSubmit={t => submit(t).then(r => this.setState({ result: r }))} />
        <ReactModal isOpen={!!this.state.result}>
          <pre>
            {this.state.result}
          </pre>
        </ReactModal>
      </React.Fragment>
    );
  }
}

export default () => (
  <div>
    <SubmitView />
  </div>
);
