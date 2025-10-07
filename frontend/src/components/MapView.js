import React from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
export default function MapView({anomalies}){
  const center=[41.8781,-87.6298];
  return (
    <MapContainer center={center} zoom={12} style={{height:'100%',width:'100%'}}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"/>
      {anomalies.map((a,i)=>{
        const lat = a.lat || 41.88 + (Math.random()-0.5)*0.05;
        const lon = a.lon || -87.63 + (Math.random()-0.5)*0.05;
        const intensity = Math.min(Math.max(a.score||0.5,0.1),1);
        return <CircleMarker key={i} center={[lat,lon]} radius={8+intensity*10} pathOptions={{color:intensity>0.8?'red':'orange'}} >
          <Popup><div><b>{a.segment}</b><div>{a.ts}</div></div></Popup>
        </CircleMarker>
      })}
    </MapContainer>
  )
}
