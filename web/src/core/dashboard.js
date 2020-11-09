import { utimes } from 'fs';
import React, { useState, useEffect } from 'react';
import PivotTableUI from 'react-pivottable/PivotTableUI';
import './dashboard.css';
import {bearerHeader} from '../util/auth'
// see documentation for supported input formats

export function Dashboard() {
  const [data, setData] = useState([{}]);
  const [props, setProps] = useState(null);

  useEffect(() => {
    const requestOptions = { method: 'GET', headers: bearerHeader() };
    fetch('/score',requestOptions)
      .then(result => result.json())
      .then(rowData => setData(rowData));
  }, [localStorage.auth]);

  return (
    <div class="pivottablemycontainer">
      <PivotTableUI
        data={data}
        vals={['score']}
        rows={['username']}
        cols={['problem_name']}
        aggregatorName={'Integer Sum'}
        rendererName={'Table Heatmap'}
        
        tableColorScaleGenerator= {function redColorScaleGenerator(values) {
            var min = Math.min.apply(Math, values);
            var max = Math.max.apply(Math, values);
            return function (x) {
              // eslint-disable-next-line no-magic-numbers
              var percentage = (x-min)/(max-min);
              var red = Math.round(255- 70*percentage)
              var green = Math.round(255*percentage)
              return { backgroundColor: 'rgb('+red+',' + green + ',' + 0 + ')' };
            };
          }
        }
        
        onChange={setProps}
        {...props}
      />
    </div>
  );
}
