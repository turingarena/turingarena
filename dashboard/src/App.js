import React, { useState,useEffect } from 'react';
import ReactDOM from 'react-dom';
import PivotTableUI from 'react-pivottable/PivotTableUI';
import PivotTable from 'react-pivottable/PivotTable'
import TableRenderers from 'react-pivottable/TableRenderers'
import aggregators from 'react-pivottable/Utilities'
import 'react-pivottable/pivottable.css';

// see documentation for supported input formats

const App = () => {

    const [data,setData] = useState([{}])
    const [props,setProps] = useState(null)

    useEffect(() => {
        fetch('http://localhost:9090/score')
        .then(result => result.json())
        .then(rowData => setData(rowData))
    }, []);

 
    
    return (
        <>
        <PivotTableUI
            data={data}
            vals={["score"]}
            rows={["username"]}
            cols={["problem_name"]}
            aggregatorName={"Maximum"}
            rendererName={"Table Heatmap"}
            onChange={s => setProps(s)}
            {...props}
        />



</>
    );
    
}

export default App;