import React, {useState} from 'react';
import MapView from './MapView';
import AnomalyStream from './AnomalyStream';
export default function Dashboard(){
  const [anomalies, setAnomalies] = useState([]);
  return (
    <div style={{display:'flex',height:'100%'}}>
      <div style={{flex:2}}>
        <MapView anomalies={anomalies}/>
      </div>
      <div style={{width:350,padding:8,overflow:'auto',background:'#f7fafc'}}>
        <h3>Live Anomalies</h3>
        <AnomalyStream onAnomaly={a=>setAnomalies(prev=>[a,...prev].slice(0,200))}/>
        {anomalies.map((a,i)=>(
          <div key={i} style={{border:'1px solid #eee',padding:6,marginTop:6}}>
            <div><b>{a.segment}</b></div>
            <div>{a.ts}</div>
            <pre style={{fontSize:11}}>{JSON.stringify(a.details)}</pre>
          </div>
        ))}
      </div>
    </div>
  )
}
