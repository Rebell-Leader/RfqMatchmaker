import { EmailTemplate } from "@shared/schema";

/**
 * Generate a PDF from an email template
 * Uses jsPDF to generate a PDF document
 * 
 * @param emailTemplate The email template to convert to PDF
 * @returns A Blob containing the PDF document
 */
export async function generatePdfFromEmail(emailTemplate: EmailTemplate): Promise<Blob> {
  // Dynamically import jsPDF to avoid server-side loading issues
  const { jsPDF } = await import('jspdf');
  
  // Create a new PDF document
  const doc = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4'
  });
  
  // Set up font sizes and margins
  const pageWidth = doc.internal.pageSize.getWidth();
  const margin = 20;
  const contentWidth = pageWidth - (margin * 2);
  
  // Set initial position
  let y = 20;
  
  // Add title
  doc.setFontSize(16);
  doc.setFont('helvetica', 'bold');
  doc.text('RFQ Proposal', margin, y);
  y += 10;
  
  // Add metadata
  doc.setFontSize(11);
  doc.setFont('helvetica', 'normal');
  doc.text(`To: ${emailTemplate.to}`, margin, y);
  y += 7;
  
  if (emailTemplate.cc) {
    doc.text(`CC: ${emailTemplate.cc}`, margin, y);
    y += 7;
  }
  
  doc.text(`Subject: ${emailTemplate.subject}`, margin, y);
  y += 10;
  
  // Add horizontal line
  doc.setDrawColor(200, 200, 200);
  doc.line(margin, y, pageWidth - margin, y);
  y += 10;
  
  // Add body - split into lines
  doc.setFontSize(10);
  
  // Format body with line breaks (max 70 chars per line)
  const lines = formatTextToLines(emailTemplate.body, 90);
  
  // Add each line to the document
  lines.forEach(line => {
    // If text would go beyond page, add a new page
    if (y > 270) {
      doc.addPage();
      y = 20;
    }
    
    doc.text(line, margin, y);
    y += 5;
  });
  
  // Return as blob
  return doc.output('blob');
}

/**
 * Format text into lines with a maximum width
 * 
 * @param text The text to format
 * @param maxChars Maximum characters per line
 * @returns An array of lines
 */
function formatTextToLines(text: string, maxChars: number): string[] {
  const paragraphs = text.split('\n');
  const lines: string[] = [];
  
  paragraphs.forEach(paragraph => {
    // Skip empty paragraphs
    if (paragraph.trim() === '') {
      lines.push('');
      return;
    }
    
    // Split paragraph into words
    const words = paragraph.split(' ');
    let currentLine = '';
    
    words.forEach(word => {
      // If adding this word would exceed max chars, start a new line
      if ((currentLine + ' ' + word).length > maxChars && currentLine.length > 0) {
        lines.push(currentLine);
        currentLine = word;
      } else {
        // Add word to current line
        currentLine = currentLine.length === 0 ? word : currentLine + ' ' + word;
      }
    });
    
    // Add the last line
    if (currentLine.length > 0) {
      lines.push(currentLine);
    }
  });
  
  return lines;
}