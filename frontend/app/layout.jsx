import './globals.css';
export const metadata = {
  title: 'AgriTech — Smarter farming, better decisions',
  description: 'Agricultural intelligence dashboard and crop decision reports.',
  icons: { icon: '/favicon.svg' }
};
export default function RootLayout({ children }) {
  return <html lang="en"><body>{children}</body></html>;
}
