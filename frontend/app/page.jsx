import Link from 'next/link';
import { ArrowRight, CloudSun, FileText, LineChart, ShieldCheck } from 'lucide-react';
import Nav from '../components/Nav';
import Footer from '../components/Footer';
export default function Home() {
  return <div className="page-shell"><Nav active="home"/>
    <main>
      <section className="hero"><div className="container hero-grid">
        <div className="reveal">
          <div className="eyebrow"><ShieldCheck size={13}/> Agriculture, simplified</div>
          <h1>Grow with <span>clarity.</span> Decide with confidence.</h1>
          <p>AgriTech turns field inputs, weather context, soil signals and farm economics into one practical crop decision report.</p>
          <div className="hero-actions">
            <Link href="/dashboard" className="btn btn-primary">Open dashboard <ArrowRight size={17}/></Link>
            <Link href="/reports" className="btn btn-secondary">View saved reports</Link>
          </div>
        </div>
        <div className="hero-visual reveal">
          <div className="hero-badge"><strong>One field. One clear plan.</strong><p>Analyze crop health, estimate yield, compare sell/store options and get an actionable recommendation.</p></div>
        </div>
      </div></section>

      <section className="section"><div className="container">
        <div className="section-head"><div><div className="eyebrow">Built for decisions</div><h2 style={{marginTop:10}}>Everything important, in one place.</h2></div><p>Minimal input. Rich context. A farmer-friendly report you can review, save and download.</p></div>
        <div className="feature-grid">
          <div className="card feature-card"><div className="icon-box"><LineChart size={21}/></div><h3>Yield intelligence</h3><p>Combines farm details and the existing server-side model to surface a predicted yield figure.</p></div>
          <div className="card feature-card"><div className="icon-box"><CloudSun size={21}/></div><h3>Weather-aware</h3><p>Uses the server workflow’s live forecast context to summarize upcoming conditions for practical decisions.</p></div>
          <div className="card feature-card"><div className="icon-box"><FileText size={21}/></div><h3>Decision report</h3><p>See disease risk, soil estimates, revenue scenarios and the final plan in a clear, printable layout.</p></div>
        </div>
      </div></section>
    </main>
    <Footer/>
  </div>;
}
