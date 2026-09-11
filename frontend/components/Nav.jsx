import Link from 'next/link';
import { BarChart3, History, Leaf } from 'lucide-react';
import Logo from './Logo';
export default function Nav({ active='' }) {
  return <nav className="nav"><div className="container nav-inner">
    <Link href="/"><Logo /></Link>
    <div className="nav-links">
      <Link className={`nav-link ${active==='home'?'active':''}`} href="/">Home</Link>
      <Link className={`nav-link ${active==='dashboard'?'active':''}`} href="/dashboard"><BarChart3 size={16}/> Dashboard</Link>
      <Link className={`nav-link ${active==='reports'?'active':''}`} href="/reports"><History size={16}/> Reports</Link>
    </div>
    <Link className="nav-cta" href="/dashboard"><Leaf size={16}/> Start analysis</Link>
  </div></nav>;
}
