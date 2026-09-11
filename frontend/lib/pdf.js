export async function downloadReportPdf(element, filename='agritech-report.pdf') {
  const [{ default: html2canvas }, { jsPDF }] = await Promise.all([import('html2canvas'), import('jspdf')]);
  const canvas = await html2canvas(element, { scale: 1.8, backgroundColor: '#f7f4ec', useCORS: true });
  const img = canvas.toDataURL('image/png');
  const pdf = new jsPDF({ orientation:'p', unit:'mm', format:'a4' });
  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const margin = 8;
  const usable = pageWidth - margin*2;
  const ratio = usable / canvas.width;
  const imageH = canvas.height * ratio;
  let y = margin;
  let remaining = imageH;
  pdf.addImage(img, 'PNG', margin, y, usable, imageH);
  remaining -= pageHeight - margin*2;
  while (remaining > 0) {
    pdf.addPage();
    y = margin - (imageH - remaining);
    pdf.addImage(img, 'PNG', margin, y, usable, imageH);
    remaining -= pageHeight - margin*2;
  }
  pdf.save(filename);
}
