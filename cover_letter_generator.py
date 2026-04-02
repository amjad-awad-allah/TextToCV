import os
import sys
import json
import datetime
import docx
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.shared import OxmlElement, qn

def clean_markdown(text):
    """Removes ALL markdown artifacts."""
    if not text: return ""
    text = str(text)
    import re
    text = re.sub(r'\[\[([^\]]+)\]\(([^\)]+)\)\]\(([^\)]+)\)', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'\1', text)
    text = re.sub(r'\|\s*---+\s*\|', '', text)
    text = re.sub(r'^\|\s*|\s*\|$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*|\*', '', text)
    text = re.sub(r'__|_', '', text)
    lines = text.split('\n')
    cleaned = [s.lstrip('|').rstrip('|').strip() for s in lines if s.strip() and not (s.startswith('|') and '---' in s)]
    return '\n'.join(cleaned).strip()

def add_hyperlink(paragraph, url, text, bold=False, size=10, color='005b9f'):
    """Adds a clickable hyperlink."""
    if not url:
        run = paragraph.add_run(clean_markdown(text))
        run.font.size = Pt(size)
        if bold: run.bold = True
        return
    if not url.startswith('http'):
        url = 'https://' + url
        
    part = paragraph.part
    r_id = part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)
    hyperlink.set(qn('w:tooltip'), url)
    new_run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    rFont = OxmlElement('w:rFonts')
    rFont.set(qn('w:ascii'), 'Calibri')
    rFont.set(qn('w:hAnsi'), 'Calibri')
    rPr.append(rFont)
    c = OxmlElement('w:color')
    c.set(qn('w:val'), color)
    rPr.append(c)
    u = OxmlElement('w:u')
    u.set(qn('w:val'), 'single')
    rPr.append(u)
    if bold:
        b = OxmlElement('w:b')
        rPr.append(b)
    sz = OxmlElement('w:sz')
    sz.set(qn('w:val'), str(size * 2))
    rPr.append(sz)
    new_run.append(rPr)
    text_elem = OxmlElement('w:t')
    text_elem.set(qn('xml:space'), 'preserve')
    text_elem.text = clean_markdown(text)
    new_run.append(text_elem)
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)

def generate_cover_letter(cv_data_file="data.json", letter_data_file="cover_letter.json", output_file="Anschreiben.docx"):
    try:
        with open(cv_data_file, 'r', encoding='utf-8') as f:
            cv_data = json.load(f)
        with open(letter_data_file, 'r', encoding='utf-8') as f:
            letter_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading files: {e}")
        return

    doc = Document()
    
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(10) # Base text identical to CV
    
    # 1. Page Margins (German Standards identical to CV)
    for section in doc.sections:
        section.page_width = Mm(210)
        section.page_height = Mm(297)
        section.top_margin = Mm(15)
        section.bottom_margin = Mm(15)
        section.left_margin = Mm(25)
        section.right_margin = Mm(20)

    basics = cv_data.get("basics", {})
    recipient = letter_data.get("recipient", {})
    
    # ==========================================
    # LETTERHEAD (Identical Header to CV)
    # ==========================================
    header_table = doc.add_table(rows=1, cols=2)
    header_table.autofit = False
    header_table.columns[0].width = Inches(5.0)
    header_table.columns[1].width = Inches(2.2)
    header_table.style = None
    
    cell_left = header_table.cell(0, 0)
    p = cell_left.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    run_name = p.add_run(clean_markdown(basics.get("name", "")) + "\n")
    run_name.bold = True
    run_name.font.size = Pt(18)
    run_name.font.color.rgb = RGBColor(0, 51, 102)
    
    location = basics.get('location', {})
    city_str = f"{clean_markdown(location.get('postalCode', ''))} {clean_markdown(location.get('city', ''))}"
    address = location.get('address', '')
    if address: city_str += f" ({clean_markdown(address)})"
    contact_text = f"{clean_markdown(basics.get('email', ''))} | {clean_markdown(basics.get('phone', ''))}\n{city_str}"
    p.add_run(contact_text).font.size = Pt(9.5)
    
    profiles = basics.get("profiles", [])
    if profiles:
        p.add_run("\n")
        for i, prof in enumerate(profiles):
            url = prof.get("url", "") if isinstance(prof, dict) else prof
            if url:
                display = url.replace("https://", "").replace("http://", "").replace("www.", "").strip('/')
                add_hyperlink(p, url, display, size=9.5)
                if i < len(profiles) - 1: p.add_run(" | ").font.size = Pt(9.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(20)

    # ==========================================
    # RECIPIENT BLOCK & DATE (DIN 5008 Style)
    # ==========================================
    rec_p = doc.add_paragraph()
    rec_p.paragraph_format.space_after = Pt(15)
    
    company = clean_markdown(recipient.get('company', ''))
    person = clean_markdown(recipient.get('contact_person', ''))
    street = clean_markdown(recipient.get('address', ''))
    city = f"{clean_markdown(recipient.get('postal_code', ''))} {clean_markdown(recipient.get('city', ''))}"
    
    rec_text = f"{company}\n{person}\n{street}\n{city}"
    r_rec = rec_p.add_run(rec_text)
    r_rec.font.size = Pt(10)

    p_date = doc.add_paragraph()
    p_date.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_date.paragraph_format.space_after = Pt(20)
    now = datetime.datetime.now()
    date_str = f"{clean_markdown(letter_data.get('location', 'Essen'))}, den {now.strftime('%d.%m.%Y')}"
    run_date = p_date.add_run(date_str)
    run_date.font.size = Pt(10)

    # ==========================================
    # SUBJECT LINE
    # ==========================================
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(15)
    run_sub = p_sub.add_run(clean_markdown(letter_data.get('subject', 'Bewerbung')))
    run_sub.bold = True
    run_sub.font.size = Pt(11)
    run_sub.font.color.rgb = RGBColor(0, 51, 102)

    # ==========================================
    # SALUTATION & BODY
    # ==========================================
    p_sal = doc.add_paragraph(clean_markdown(letter_data.get('salutation', 'Sehr geehrte Damen und Herren,')))
    p_sal.paragraph_format.space_after = Pt(8)

    for para in letter_data.get('paragraphs', []):
        p_body = doc.add_paragraph(clean_markdown(para))
        p_body.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_body.paragraph_format.space_after = Pt(8)
        p_body.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE

    # ==========================================
    # CLOSING & SIGNATURE
    # ==========================================
    doc.add_paragraph().paragraph_format.space_after = Pt(10)
    p_close = doc.add_paragraph(clean_markdown(letter_data.get('closing', 'Mit freundlichen Grüßen')))
    p_close.paragraph_format.space_after = Pt(30) # Space for hand signature if printed

    p_sig = doc.add_paragraph()
    r_sig = p_sig.add_run(clean_markdown(basics.get("name", "")))
    r_sig.bold = True
    r_sig.font.size = Pt(10)

    try:
        doc.save(output_file)
        print(f"✅ Erfolg! {output_file} wurde generiert passend zum CV-Design.")
    except Exception as e:
        print(f"❌ Fehler beim Speichern: {e}")

if __name__ == "__main__":
    cv_input = "data.json"
    letter_input = "cover_letter.json"
    word_output = "Anschreiben.docx"
    if len(sys.argv) >= 2: cv_input = sys.argv[1]
    if len(sys.argv) >= 3: letter_input = sys.argv[2]
    if len(sys.argv) >= 4: word_output = sys.argv[3]
    generate_cover_letter(cv_input, letter_input, word_output)
