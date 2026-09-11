'use client';
import { useEffect, useMemo, useState } from 'react';
import { CalendarDays, Crosshair, ImagePlus, LoaderCircle, MapPin, Radio, Sparkles } from 'lucide-react';
import Nav from '../../components/Nav';
import Footer from '../../components/Footer';
import { fetchSensor, generateReport } from '../../lib/api';
import { saveReport } from '../../lib/storage';
import { useRouter } from 'next/navigation';

const defaults = { item:'', growth:'Vegetative', sowing_date:'', current_date:new Date().toISOString().slice(0,10),
  average_rain_fall_mm_per_year:'800', pesticides_tonnes:'0.2', avg_temp:'25', lat:'23.5937', lon:'80.9629',
  storage_availability:'Moderate', disease_detect:false, crop_img:'', soil_img:'', temp:'27', humidity:'65', moisture:'42', dryness:'28', raining:false };

export default function Dashboard() {
  const router = useRouter();
  const [form,setForm]=useState(defaults);
  const [sensor,setSensor]=useState(null);
  const [loading,setLoading]=useState(false);
  const [detecting,setDetecting]=useState(false);
  const [msg,setMsg]=useState('');
  const [error,setError]=useState('');

  useEffect(()=>{
    const loadSensor = () => fetchSensor().then(setSensor).catch(()=>{});
    loadSensor();
    const interval = setInterval(loadSensor, 3000);
    return () => clearInterval(interval);
  },[]);

  useEffect(()=>{ if(sensor) setForm(f=>({...f,temp:String(sensor.temp),humidity:String(sensor.humidity),moisture:String(sensor.moisture),dryness:sensor.ambidientLight != null ? String(sensor.ambidientLight) : f.dryness,raining:Boolean(sensor.raining)})); },[sensor]);
  const set=(k,v)=>setForm(f=>({...f,[k]:v}));

  const pickImage = (key) => {
    const input = document.createElement('input');
    input.type='file'; input.accept='image/*';
    input.onchange = () => {
      const file=input.files?.[0]; if(!file) return;
      // Server contract requires a URL. Object URLs work for preview but are not
      // fetchable by the remote server, so we keep an explicit URL field for production.
      const objectUrl = URL.createObjectURL(file);
      set(`${key}_preview`, objectUrl);
      setMsg(`${key === 'soil_img' ? 'Soil' : 'Crop'} photo selected for preview. Enter a public image URL in the URL field so the server can analyze it.`);
    };
    input.click();
  };

  const locate=()=>{
    if(!navigator.geolocation){ setError('Geolocation is not supported by this browser.'); return; }
    setDetecting(true); setError('');
    navigator.geolocation.getCurrentPosition(pos=>{
      set('lat',pos.coords.latitude.toFixed(6)); set('lon',pos.coords.longitude.toFixed(6)); setDetecting(false);
    },()=>{setError('Location access was denied.');setDetecting(false);},{enableHighAccuracy:true,timeout:10000});
  };

  async function submit(e){
    e.preventDefault(); setLoading(true); setError(''); setMsg('');
    try {
      const payload = {
        temp:Number(form.temp), humidity:Number(form.humidity), moisture:Number(form.moisture), dryness:Number(form.dryness),
        raining:Boolean(form.raining),
        crop_details: {
          Item: form.item, average_rain_fall_mm_per_year:Number(form.average_rain_fall_mm_per_year), avg_temp:Number(form.avg_temp),
          crop_img: form.crop_img || null, current_date:form.current_date, disease_detect:form.disease_detect, growth:form.growth,
          lat:Number(form.lat), lon:Number(form.lon), pesticides_tonnes:Number(form.pesticides_tonnes), soil_img:form.soil_img,
          sowing_date:form.sowing_date, storage_availability:form.storage_availability
        }
      };
      if(!payload.crop_details.Item || !payload.crop_details.sowing_date) throw new Error('Please provide crop name and sowing date.');
      const report=await generateReport(payload);
      const id=saveReport(report);
      router.push(`/report/${id}`);
    } catch(err){ setError(err.message || 'Unable to generate report.'); }
    finally { setLoading(false); }
  }

  return <div className="page-shell"><Nav active="dashboard"/><main className="app-page"><div className="container">
    <div className="page-heading"><div className="eyebrow"><Sparkles size={13}/> Crop intelligence</div><h1>New crop analysis</h1><p>Enter the field details, connect sensor context and generate one structured decision report.</p></div>
    <div className="dashboard-grid">
      <form className="card form-card" onSubmit={submit}>
        <div className="section-head" style={{marginBottom:16}}><div><h2 style={{fontSize:22}}>Field details</h2><p style={{fontSize:13,marginTop:6}}>These fields map directly to the existing FastAPI contract.</p></div></div>
        <div className="form-grid">
          <div className="field"><label>Crop name</label><input value={form.item} onChange={e=>set('item',e.target.value)} placeholder="e.g. Wheat"/></div>
          <div className="field"><label>Growth stage</label><select value={form.growth} onChange={e=>set('growth',e.target.value)}>{['Seedling','Vegetative','Flowering','Fruiting','Harvest'].map(x=><option key={x}>{x}</option>)}</select></div>
          <div className="field"><label>Sowing date</label><input type="date" value={form.sowing_date} onChange={e=>set('sowing_date',e.target.value)}/></div>
          <div className="field"><label>Current date</label><input type="date" value={form.current_date} onChange={e=>set('current_date',e.target.value)}/></div>
          <div className="field"><label>Avg. rainfall (mm/year)</label><input type="number" value={form.average_rain_fall_mm_per_year} onChange={e=>set('average_rain_fall_mm_per_year',e.target.value)}/></div>
          <div className="field"><label>Avg. temperature °C</label><input type="number" step="0.1" value={form.avg_temp} onChange={e=>set('avg_temp',e.target.value)}/></div>
          <div className="field"><label>Pesticides (tonnes)</label><input type="number" step="0.01" value={form.pesticides_tonnes} onChange={e=>set('pesticides_tonnes',e.target.value)}/></div>
          <div className="field"><label>Storage availability</label><select value={form.storage_availability} onChange={e=>set('storage_availability',e.target.value)}>{['Low','Moderate','High'].map(x=><option key={x}>{x}</option>)}</select></div>

          <div className="field"><label>Latitude</label><input value={form.lat} onChange={e=>set('lat',e.target.value)} /></div>
          <div className="field"><label>Longitude</label><input value={form.lon} onChange={e=>set('lon',e.target.value)} /></div>
          <div className="field full"><button type="button" className="btn btn-secondary" onClick={locate} disabled={detecting}>{detecting?<LoaderCircle className="spin" size={16}/>:<MapPin size={16}/>} {detecting?'Detecting…':'Detect my location'}</button></div>

          <div className="field full">
            <label>Soil image URL <span className="hint">(required by server)</span></label>
            <input value={form.soil_img} onChange={e=>set('soil_img',e.target.value)} placeholder="https://.../soil.jpg"/>
            <div className="hint">The backend fetches this URL directly for soil analysis. Use a public image URL when connected.</div>
            {form.soil_img && <div className="preview"><img src={form.soil_img} alt="Soil preview" onError={e=>e.currentTarget.style.display='none'}/></div>}
          </div>
          <div className="field full">
            <label>Crop image URL <span className="hint">(required when disease detection is enabled)</span></label>
            <input value={form.crop_img} onChange={e=>set('crop_img',e.target.value)} placeholder="https://.../crop.jpg"/>
            {form.crop_img && <div className="preview"><img src={form.crop_img} alt="Crop preview" onError={e=>e.currentTarget.style.display='none'}/></div>}
          </div>
          <div className="field">
            <div className="check-row">
              <input
                id="dd"
                type="checkbox"
                checked={form.disease_detect}
                onChange={e=>set('disease_detect',e.target.checked)}
              />
              <label htmlFor="dd">Include image-based crop disease analysis</label>
            </div>
          </div>

          <div className="field">
            <div className="check-row">
              <input
                id="raining"
                type="checkbox"
                checked={form.raining}
                onChange={e=>set('raining',e.target.checked)}
              />
              <label htmlFor="raining">Is it raining?</label>
            </div>
          </div>

          <div className="field">
            <label>Sensor temperature °C</label>
            <input type="number" step="0.1" value={form.temp} onChange={e=>set('temp',e.target.value)}/>
          </div>

          <div className="field">
            <label>Sensor humidity %</label>
            <input type="number" step="0.1" value={form.humidity} onChange={e=>set('humidity',e.target.value)}/>
          </div>

          <div className="field">
            <label>Sensor moisture %</label>
            <input type="number" step="0.1" value={form.moisture} onChange={e=>set('moisture',e.target.value)}/>
          </div>

          <div className="field">
            <label>Ambient Light (lux)</label>
            <input type="number" step="0.1" value={form.dryness} onChange={e=>set('dryness',e.target.value)}/>
          </div>
        </div>
        {msg && <div className="status info">{msg}</div>}
        {error && <div className="status error">{error}</div>}
        <div className="actions"><button className="btn btn-primary" disabled={loading}>{loading?<><LoaderCircle className="spin" size={17}/> Generating…</>:<><Sparkles size={17}/> Generate report</>}</button></div>
      </form>

      <aside className="side-stack">
        <div className="card sensor-card">
          <div className="sensor-head"><div><strong>Sensor context</strong><div className="hint" style={{marginTop:4}}>ESP32 / device sensor values</div></div><span className="pill">{sensor?'LIVE':'MANUAL'}</span></div>
          <div className="sensor-grid">
            <div className="metric"><span>Temperature</span><strong>{form.temp}°</strong></div>
            <div className="metric"><span>Humidity</span><strong>{form.humidity}%</strong></div>
            <div className="metric"><span>Moisture</span><strong>{form.moisture}%</strong></div>
            <div className="metric"><span>Ambient Light</span><strong>{form.dryness} lux</strong></div>
            <div className="metric"><span>Rain</span><strong>{form.raining ? 'Raining' : 'Not raining'}</strong></div>
          </div>
          {sensor ? <div className="hint" style={{marginTop:12}}><Radio size={13} style={{verticalAlign:'-2px'}}/> Synced from /sensor-data/esp32-1</div> : <div className="hint" style={{marginTop:12}}>No live reading found — manual values stay editable.</div>}
        </div>
        <div className="card tips-card">
          <div className="sensor-head"><strong>Before you generate</strong><CalendarDays size={17}/></div>
          <div className="tips-list">
            <div className="tip">• Use a public soil image URL so the current backend can download it.</div>
            <div className="tip">• Turn on disease detection only when you also provide a crop image URL.</div>
            <div className="tip">• Location is used by the server workflow for weather context and revenue estimation.</div>
          </div>
        </div>
      </aside>
    </div>
  </div></main><Footer/></div>;
}