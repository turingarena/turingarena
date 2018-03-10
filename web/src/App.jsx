import PropTypes from 'prop-types';
import './App.css';

const UploadView = ({ onSubmit }) => (
  <form onSubmit={(e) => { onSubmit(e.target); e.preventDefault(); }}>
    <input type="file" name="solution_file" />
    <select name="language">
      <option>C/C++</option>
      <option>Python</option>
      <option>Java</option>
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
