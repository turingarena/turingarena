import PropTypes from 'prop-types';
import './App.css';

const UploadView = ({ onSubmit }) => (
  <form onSubmit={(e) => { onSubmit(e.target); e.preventDefault(); }}>
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
  fetch(process.env.TURINGARENA_EVALUATE_ENDPOINT, {
    method: 'post',
    body: new FormData(form),
  }).then((response) => {
    console.log(response);
  });
};

const SubmitView = () => (
  <UploadView onSubmit={submit} />
);

export default () => (
  <div>
    <SubmitView />
  </div>
);
