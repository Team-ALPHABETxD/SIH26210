 'use client';
import { useEffect, useRef, useState } from 'react';
import { ArrowLeft, Download, ExternalLink, Leaf, LoaderCircle, ShieldAlert, Sprout, TrendingUp, Warehouse } from 'lucide-react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import Nav from '../../../components/Nav';
import Footer from '../../../components/Footer';
import { getReport } from '../../../lib/storage';
import { downloadReportPdf } from '../../../lib/pdf';

function money(v){ return typeof v==='number' ? `₹${Math.round(v).toLocaleString('en-IN')}` : '—'; }
function pct(v){ return typeof v==='number' ? `${Math.round(v*100)}%` : '—'; }

export default function ReportPage() {
  const { id } = useParams();
  const [item,setItem]=useState(null);
  const ref=useRef(null);

  useEffect(()=>setItem(getReport(id)),[id]);
  const r=item?.report || {};
  const crop=r.crop_details||{};
  const plan=r.plan||{};
  const disease=r.disease_details||{};
  const soil=r.soil_details||{};
  const revenue=r.rev_strat_details?.rev_stats||[];
  const weather=r.weather_details||{};
  const control=r.control_strats?.steps||[];

  const yieldValue = typeof r.predicted_yeild==='number' ? r.predicted_yeild : Number(r.predicted_yeild || 0);
  const bestRevenue = revenue.reduce((a,b)=>(!a || (b.rev-b.exp)>(a.rev-a.exp))?b:a,null);

  if(item===null) return <div className="page-shell"><Nav active="reports"/><main className="app-page"><div className="container empty"><LoaderCircle className="spin" style={{margin:'0 auto 10px'}}/>Loading report…</div></main></div>;
  if(!item) return <div className="page-shell"><Nav active="reports"/><main className="app-page"><div className="container empty">Report not found. <Link href="/dashboard" style={{color:'var(--leaf)',fontWeight:700}}>Create a new analysis</Link>.</div></main><Footer/></div>;

  return <div className="page-shell"><Nav active="reports"/><main className="app-page"><div className="container">
    <div className="report-top"><div><Link href="/reports" className="btn btn-secondary"><ArrowLeft size={16}/> All reports</Link></div><div className="report-actions"><button className="btn btn-primary" onClick={()=>downloadReportPdf(ref.current,`agritech-${(crop.Item||'crop').toLowerCase().replace(/\s+/g,'-')}-report.pdf`)}><Download size={16}/> Download PDF</button></div></div>

    <div ref={ref}>
      <div className="summary-banner"><div className="kicker">AgriTech crop report</div><h2>{crop.Item || 'Crop analysis'} · {plan.decision || 'Decision pending'}</h2><p>{plan.reason || 'A structured report has been generated from your farm inputs, weather context, disease assessment, revenue scenarios and yield prediction.'}</p></div>

      <div className="report-grid">
        <div className="card r-card span-4"><div className="r-title"><h3><Sprout size={16}/> Crop profile</h3></div><div className="kv-grid">
          <div className="kv"><span>Growth</span><strong>{crop.growth||'—'}</strong></div><div className="kv"><span>Storage</span><strong>{crop.storage_availability||'—'}</strong></div>
          <div className="kv"><span>Sowing</span><strong>{crop.sowing_date||'—'}</strong></div><div className="kv"><span>Location</span><strong>{crop.lat?.toFixed?.(3) ?? crop.lat}, {crop.lon?.toFixed?.(3) ?? crop.lon}</strong></div>
        </div></div>

        <div className="card r-card span-4"><div className="r-title"><h3><TrendingUp size={16}/> Predicted yield</h3></div><div style={{fontFamily:'Manrope',fontSize:38,fontWeight:800}}>{yieldValue ? yieldValue.toFixed(2) : '—'}</div><div className="hint" style={{marginTop:5}}>Server model output</div></div>

        <div className={`card r-card span-4 ${disease.NA===false?'danger':'good'}`}><div className="r-title"><h3><ShieldAlert size={16}/> Disease outlook</h3></div><div style={{fontFamily:'Manrope',fontSize:24,fontWeight:800}}>{disease.NA===false ? (disease.name||'Potential disease') : 'No disease predicted'}</div><div style={{marginTop:6,fontSize:13,lineHeight:1.6,opacity:.85}}>{disease.NA===false ? `${disease.status || ''} · Spoilage risk: ${disease.spoilage_risk||'—'} · Confidence: ${pct(disease.confidence)}` : 'The server workflow did not flag meaningful disease evidence.'}</div></div>

        <div className="card r-card span-6"><div className="r-title"><h3><Leaf size={16}/> Soil snapshot</h3></div><div className="kv-grid">
          <div className="kv"><span>N</span><strong>{soil.N ?? '—'}</strong></div><div className="kv"><span>P</span><strong>{soil.P ?? '—'}</strong></div>
          <div className="kv"><span>K</span><strong>{soil.K ?? '—'}</strong></div><div className="kv"><span>pH</span><strong>{soil.pH ?? '—'}</strong></div>
        </div><div className="hint" style={{marginTop:12}}>{soil.notes||'Visual soil analysis note unavailable.'}</div></div>

        <div className="card r-card span-6"><div className="r-title"><h3><CloudIcon/> Weather outlook</h3></div><p style={{lineHeight:1.65,color:'var(--muted)'}}>{weather.summary||'Weather summary unavailable.'}</p></div>

        <div className="card r-card span-12"><div className="r-title"><h3><Warehouse size={16}/> Revenue scenarios</h3><span className="pill">{bestRevenue?`Best margin: ${bestRevenue.name}`:'No scenarios'}</span></div>
          <div className="bars">{revenue.map((x,i)=>{const max=Math.max(...revenue.map(v=>Math.max(1,v.rev||0)),1); return <div className="bar-group" key={x.name||i}><div className="bar-stack"><div className="bar" style={{height:`${Math.max(10,((x.rev||0)/max)*145)}px`}}></div><div className="bar alt" style={{height:`${Math.max(8,((x.exp||0)/max)*145)}px`}}></div></div><div className="bar-label">{x.name}</div><div className="hint">{money(x.rev)} / {money(x.exp)}</div></div>})}</div>
        </div>

        {disease.NA===false && control.length>0 && <div className="card r-card span-12"><div className="r-title"><h3>Recommended disease-control actions</h3></div><ol className="control-list">{control.map((s,i)=><li key={i}>{s}</li>)}</ol></div>}

        <div className="card r-card span-8"><div className="r-title"><h3>Why this decision?</h3></div><p style={{lineHeight:1.7,color:'var(--muted)'}}>{plan.reason||'No decision rationale returned.'}</p></div>
        <div className="card r-card span-4"><div className="r-title"><h3>Next step</h3></div><p style={{lineHeight:1.65,color:'var(--muted)'}}>{plan.decision==='Sell'?'Prepare the harvest for market and monitor prices.':plan.decision==='Store'?'Use available storage capacity and monitor market conditions.':plan.decision==='Disease Control'?'Prioritize the control steps above before maximizing sales.':'Review the generated details with your field context.'}</p></div>
      </div>
    </div>
  </div></main><Footer/></div>;
}

function CloudIcon(){ return <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17.5 19H9a7 7 0 1 1 6.6-9.4A4.5 4.5 0 0 1 17.5 19Z"/></svg>; }
