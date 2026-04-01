import os
import json
import datetime
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH

def generate_cover_letter(cv_data_file="data.json", letter_data_file="cover_letter.json", output_file="Anschreiben.docx"):
    try:
        with open(cv_data_file, 'r', encoding='utf-8') as f:
            cv_data = json.load(f)
        with open(letter_data_file, 'r', encoding='utf-8') as f:
            letter_data = json.load(f)
    except Exception as e:
        print(f"Error loading files: {e}")
        return

    doc = Document()
    
    # 1. Page Margins (German Standards approx)
    section = doc.sections[0]
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)
    
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)

    basics = cv_data.get("basics", {})
    recipient = letter_data.get("recipient", {})
    
    # Header - Same UI Spirit as CV
    header_table = doc.add_table(rows=1, cols=2)
    header_table.autofit = False
    header_table.columns[0].width = Inches(4.5)
    header_table.columns[1].width = Inches(2.5)

    # Sender Name & Address (CV Spirit Header)
    cell_sender = header_table.cell(0, 0)
    p = cell_sender.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    run_name = p.add_run(basics.get("name", "").upper() + "\n")
    run_name.bold = True
    run_name.font.size = Pt(20)
    run_name.font.color.rgb = RGBColor(0, 51, 102)

    location = basics.get('location', {})
    address = f"{location.get('address', '')}, {location.get('postalCode', '')} {location.get('city', '')}"
    contact = f"{basics.get('email', '')} | {basics.get('phone', '')}"
    
    run_info = p.add_run(f"{address}\n{contact}")
    run_info.font.size = Pt(9)
    run_info.font.color.rgb = RGBColor(100, 100, 100)

    # Date Block
    cell_date = header_table.cell(0, 1)
    p_date = cell_date.paragraphs[0]
    p_date.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    now = datetime.datetime.now()
    date_str = f"{letter_data.get('location', 'Essen')}, {now.strftime('%d.%m.%Y')}"
    run_date = p_date.add_run(date_str)
    run_date.font.size = Pt(10)
    run_date.italic = True

    doc.add_paragraph().paragraph_format.space_after = Pt(20)

    # Recipient Block
    p_rec = doc.add_paragraph()
    p_rec.paragraph_format.space_after = Pt(15)
    rec_text = (
        f"{recipient.get('company', '')}\n"
        f"{recipient.get('contact_person', '')}\n"
        f"{recipient.get('address', '')}\n"
        f"{recipient.get('postal_code', '')} {recipient.get('city', '')}"
    )
    r_rec = p_rec.add_run(rec_text)
    r_rec.font.size = Pt(10)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # Subject Line
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(15)
    run_sub = p_sub.add_run(letter_data.get('subject', ''))
    run_sub.bold = True
    run_sub.font.size = Pt(12)
    run_sub.font.color.rgb = RGBColor(0, 51, 102)

    # Salutation
    p_sal = doc.add_paragraph(letter_data.get('salutation', 'Sehr geehrte Damen und Herren,'))
    p_sal.paragraph_format.space_after = Pt(10)

    # Body Paragraphs
    for para in letter_data.get('paragraphs', []):
        p_body = doc.add_paragraph(para)
        p_body.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_body.paragraph_format.space_after = Pt(10)
        p_body.paragraph_format.line_spacing = 1.15

    # Closing
    doc.add_paragraph().paragraph_format.space_after = Pt(10)
    p_close = doc.add_paragraph(letter_data.get('closing', 'Mit freundlichen Grüßen'))
    p_close.paragraph_format.space_after = Pt(5)

    # Signature
    p_sig = doc.add_paragraph()
    r_sig = p_sig.add_run(basics.get("name", ""))
    r_sig.bold = True
    r_sig.font.size = Pt(11)

    try:
        doc.save(output_file)
        print(f"Erfolg! {output_file} wurde generiert.")
    except Exception as e:
        print(f"Fehler beim Speichern: {e}")

if __name__ == "__main__":
    generate_cover_letter()
