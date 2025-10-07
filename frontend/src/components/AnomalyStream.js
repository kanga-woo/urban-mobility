import React, {useEffect, useRef} from 'react';
export default function AnomalyStream({onAnomaly}){
  const esRef = useRef(null);
  useEffect(()=>{
    const url = (process.env.REACT_APP_API_URL || 'http://localhost:8000') + '/anomalies/stream';
    const es = new EventSource(url);
    es.addEventListener('anomaly', e=>{
      try{ const d = JSON.parse(e.data); onAnomaly(d);}catch(err){console.error(err)}
    });
    es.onerror = ()=>{console.warn('SSE error')};
    esRef.current = es;
    return ()=> es.close();
  },[onAnomaly]);
  return <div>Connected</div>
}
