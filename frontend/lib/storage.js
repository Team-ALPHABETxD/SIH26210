const KEY = 'agritech_reports_v1';
export function getReports() {
  if (typeof window === 'undefined') return [];
  try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch { return []; }
}
export function saveReport(report) {
  if (typeof window === 'undefined') return;
  const list = getReports();
  const item = { id: crypto.randomUUID(), createdAt: new Date().toISOString(), report };
  localStorage.setItem(KEY, JSON.stringify([item, ...list].slice(0, 20)));
  return item.id;
}
export function getReport(id) {
  const item = getReports().find(x=>x.id===id) || null;
  if (!item) return null;
  // Support both the current normalized format and older saved responses
  // that stored the backend {status, report} wrapper.
  if (item.report?.report && typeof item.report.report === 'object') {
    return { ...item, report: item.report.report };
  }
  return item;
}
