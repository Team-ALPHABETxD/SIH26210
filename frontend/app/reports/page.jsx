 'use client';
import { useEffect, useState } from 'react';
import { ArrowRight, Clock3, FileText, Plus, Trash2 } from 'lucide-react';
import Link from 'next/link';
import Nav from '../../components/Nav';
import Footer from '../../components/Footer';
import { getReports } from '../../lib/storage';

export default function ReportsPage(){
  const [items,setItems]=useState([]);
  useEffect(()=>setItems(getReports()),[]);
  return <div className="page-shell"><Nav active="reports"/><main className="app-page"><div className="container">
    <div className="page-heading"><div className="eyebrow"><FileText size={13}/> Local history</div><h1>Saved reports</h1><p>Your latest analyses are kept in this browser using local storage. No account required.</p></div>
    <div className="card r-card">
      {items.length===0 ? <div className="empty">No reports yet. <div style={{marginTop:14}}><Link className="btn btn-primary" href="/dashboard"><Plus size={16}/> Create your first report</Link></div></div> :
      <div className="history-list">{items.map(x=>{const c=x.report?.crop_details||{}; const p=x.report?.plan||{}; return <div key={x.id} className="history-item"><div className="history-meta"><strong>{c.Item||'Crop report'} · {p.decision||'Analysis'}</strong><span><Clock3 size={12} style={{verticalAlign:'-2px'}}/> {new Date(x.createdAt).toLocaleString()}</span></div><Link className="btn btn-secondary" href={`/report/${x.id}`}>Open <ArrowRight size={16}/></Link></div>})}</div>}
    </div>
  </div></main><Footer/></div>;
}
