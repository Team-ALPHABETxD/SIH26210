export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
export async function fetchSensor(deviceId='esp32-1') {
  const res = await fetch(`${API_BASE}/sensor-data/${encodeURIComponent(deviceId)}`, { cache:'no-store' });
  if (!res.ok) throw new Error('No live sensor data available');
  return res.json();
}
export async function generateReport(payload) {
  const res = await fetch(`${API_BASE}/generate-report`, {
    method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)
  });
  const data = await res.json().catch(()=>({}));
  if (!res.ok) {
    const detail = typeof data?.detail === 'string' && data.detail.trim() ? data.detail : 'Report generation failed';
    throw new Error(detail);
  }
  // Backend returns { status: 'success', report: {...} }. Keep the frontend
  // state aligned with the actual report object used by the report page.
  return data?.report ?? data;
}
