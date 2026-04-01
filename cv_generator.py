import sys
import json
import docx
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml.shared import OxmlElement, qn

def add_hyperlink(paragraph, url, text, bold=False, size=10):
    part = paragraph.part
    r_id = part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)

    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)

    new_run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')

    c = OxmlElement('w:color')
    c.set(qn('w:val'), '005b9f') # subtle blue for links
    rPr.append(c)

    u = OxmlElement('w:u')
    u.set(qn('w:val'), 'single')
    rPr.append(u)

    rFont = OxmlElement('w:rFonts')
    rFont.set(qn('w:ascii'), 'Calibri')
    rFont.set(qn('w:hAnsi'), 'Calibri')
    rPr.append(rFont)

    if bold:
        b = OxmlElement('w:b')
        rPr.append(b)

    sz = OxmlElement('w:sz')
    sz.set(qn('w:val'), str(size * 2))
    rPr.append(sz)

    new_run.append(rPr)
    
    text_elem = OxmlElement('w:t')
    text_elem.text = text
    new_run.append(text_elem)

    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)

def add_page_number(run):
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')

    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = "PAGE"

    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'separate')

    t = OxmlElement('w:t')
    t.text = "1"

    fldChar3 = OxmlElement('w:fldChar')
    fldChar3.set(qn('w:fldCharType'), 'end')

    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(t)
    run._r.append(fldChar3)

def generate_cv(json_file="data.json", output_file="Generated_CV.docx"):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {json_file}. Please ensure data.json exists in the current directory.")
        return

    doc = Document()
    
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(10)
    
    sections = doc.sections
    content_width = Inches(7.0) # fallback
    
    for section in sections:
        section.page_width = Mm(210)  # A4 width
        section.page_height = Mm(297) # A4 height
        section.top_margin = Inches(0.4)
        section.bottom_margin = Inches(0.4)
        section.left_margin = Inches(0.6)
        section.right_margin = Inches(0.6)
        
        # Calculate exactly the space available for proper right alignment
        content_width = section.page_width - section.left_margin - section.right_margin
        
        footer = section.footer
        p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r = p.add_run()
        r.font.name = 'Calibri'
        r.font.size = Pt(9)
        add_page_number(r)

    def add_heading(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(2)
        h.paragraph_format.keep_with_next = True
        run = h.add_run(text)
        run.font.name = 'Calibri'
        run.font.color.rgb = RGBColor(0, 51, 102)
        run.font.size = Pt(13)
        run.font.bold = True
        return h

    table = doc.add_table(rows=1, cols=2)
    table.autofit = False
    table.columns[0].width = Inches(5.2)
    table.columns[1].width = Inches(2.0)

    cell_left = table.cell(0, 0)
    cell_right = table.cell(0, 1)

    basics = data.get("basics", {})

    p = cell_left.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    run1 = p.add_run(basics.get("name", "") + "\n")
    run1.bold = True
    run1.font.name = 'Calibri'
    run1.font.size = Pt(22)
    run1.font.color.rgb = RGBColor(0, 51, 102)

    email = basics.get('email', '')
    phone = basics.get('phone', '')
    location = basics.get('location', {})
    address_str = ", ".join([loc for loc in [location.get('address', ''), location.get('city', ''), location.get('region', '')] if loc])
    
    linkedin = ""
    github = ""
    for prof in basics.get("profiles", []):
        if prof.get("network", "").lower() == "linkedin":
            linkedin = prof.get("url", "")
        elif prof.get("network", "").lower() == "github":
            github = prof.get("url", "")
            
    website = basics.get('url', '')

    contact_parts = []
    contact_parts.append(f"{email} | {phone}".strip(' |'))
    if address_str: contact_parts.append(address_str)
    
    contact_text = "\n".join([pt for pt in contact_parts if pt]) + "\n"
    run2 = p.add_run(contact_text)
    run2.font.name = 'Calibri'
    run2.font.size = Pt(10)

    if linkedin:
        add_hyperlink(p, linkedin, linkedin.replace("https://", "").replace("www.", ""))
    if github:
        if linkedin: p.add_run(" | ")
        add_hyperlink(p, github, github.replace("https://", "").replace("www.", ""))
    if website:
        if linkedin or github: p.add_run(" | ")
        add_hyperlink(p, website, website.replace("https://", "").replace("www.", ""))

    p_right = cell_right.paragraphs[0]
    p_right.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_right.paragraph_format.space_after = Pt(0)
    placeholder_text = data.get("custom", {}).get("photo_note", "")
    placeholder = p_right.add_run(placeholder_text)
    placeholder.font.name = 'Calibri'
    placeholder.font.color.rgb = RGBColor(120, 120, 120)
    placeholder.font.italic = True

    p_hr = doc.add_paragraph()
    p_hr.add_run("_" * 68).font.color.rgb = RGBColor(200, 200, 200)
    p_hr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_hr.paragraph_format.space_after = Pt(4)

    summary = basics.get("summary", "")
    if summary:
        add_heading('PROFIL')
        p = doc.add_paragraph(summary)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_together = True
        if p.runs: 
            p.runs[0].font.name = 'Calibri'
            p.runs[0].font.size = Pt(10)

    work_items = data.get("work", [])
    if work_items:
        add_heading('BERUFSERFAHRUNG')
        for job in work_items:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.keep_with_next = True
            
            tab_stops = p.paragraph_format.tab_stops
            tab_stops.add_tab_stop(content_width, WD_TAB_ALIGNMENT.RIGHT)
            
            title = job.get('position', '')
            company = job.get('name', '')
            date_str = f"{job.get('startDate', '')} - {job.get('endDate', 'heute')}"
            
            r = p.add_run(f"{title} | {company}")
            r.bold = True
            r.font.name = 'Calibri'
            r.font.size = Pt(11)
            
            r2 = p.add_run(f"\t{date_str}")
            r2.italic = True
            r2.font.name = 'Calibri'
            r2.font.color.rgb = RGBColor(80, 80, 80)
            r2.font.size = Pt(10)
            
            summary_text = job.get('summary', '')
            if summary_text:
                sp = doc.add_paragraph(summary_text)
                sp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                sp.paragraph_format.space_after = Pt(2)
                sp.paragraph_format.keep_together = True
                sp.paragraph_format.keep_with_next = True
                if sp.runs: 
                    sp.runs[0].font.name = 'Calibri'
                    sp.runs[0].font.size = Pt(10)
            
            bullets = job.get('highlights', [])
            for i, bullet in enumerate(bullets):
                bp = doc.add_paragraph(bullet, style='List Bullet')
                bp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                bp.paragraph_format.space_after = Pt(1)
                bp.paragraph_format.keep_together = True
                if i < len(bullets) - 1:
                    bp.paragraph_format.keep_with_next = True
                if bp.runs: 
                    bp.runs[0].font.name = 'Calibri'
                    bp.runs[0].font.size = Pt(10)
            doc.add_paragraph().paragraph_format.space_after = Pt(4)

    edu_items = data.get("education", [])
    if edu_items:
        add_heading('AUSBILDUNG')
        for edu in edu_items:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.keep_with_next = True
            
            tab_stops = p.paragraph_format.tab_stops
            tab_stops.add_tab_stop(content_width, WD_TAB_ALIGNMENT.RIGHT)
            
            title = edu.get('area', '')
            institution = edu.get('institution', '')
            date_str = f"{edu.get('startDate', '')} - {edu.get('endDate', '')}"
            if date_str == " - ": date_str = ""
            
            r = p.add_run(f"{title} | {institution}")
            r.bold = True
            r.font.name = 'Calibri'
            r.font.size = Pt(11)
            
            r2 = p.add_run(f"\t{date_str}")
            r2.italic = True
            r2.font.name = 'Calibri'
            r2.font.color.rgb = RGBColor(80, 80, 80)
            r2.font.size = Pt(10)
            
            courses = edu.get('courses', [])
            if courses:
                bp = doc.add_paragraph("Fokus: " + ", ".join(courses), style='List Bullet')
                bp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                bp.paragraph_format.space_after = Pt(1)
                bp.paragraph_format.keep_together = True
                if edu.get('notes'): bp.paragraph_format.keep_with_next = True
                if bp.runs: 
                    bp.runs[0].font.name = 'Calibri'
                    bp.runs[0].font.size = Pt(10)
            
            notes = edu.get('notes', '')
            if notes:
                bp = doc.add_paragraph(notes, style='List Bullet')
                bp.paragraph_format.space_after = Pt(1)
                bp.paragraph_format.keep_together = True
                if bp.runs: 
                    bp.runs[0].font.name = 'Calibri'
                    bp.runs[0].font.size = Pt(10)
            doc.add_paragraph().paragraph_format.space_after = Pt(4)

    skills_items = data.get("skills", [])
    if skills_items:
        add_heading('TECHNISCHE KENNTNISSE')
        for skill in skills_items:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.keep_together = True
            category = skill.get('name', '')
            r = p.add_run(f"• {category}: ")
            r.bold = True
            r.font.name = 'Calibri'
            r.font.size = Pt(10)
            details = ", ".join(skill.get('keywords', []))
            r2 = p.add_run(details)
            r2.font.name = 'Calibri'
            r2.font.size = Pt(10)

    projects_items = data.get("projects", [])
    if projects_items:
        add_heading('PROJEKTE (AUSWAHL)')
        for proj in projects_items:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.keep_with_next = True
            
            url = proj.get('url', '')
            if url:
                add_hyperlink(p, url, proj.get('name', ''), bold=True, size=11)
            else:
                r1 = p.add_run(proj.get('name', ''))
                r1.bold = True
                r1.font.name = 'Calibri'
                r1.font.size = Pt(11)
            
            desc = proj.get('description', '')
            if desc:
                bp = doc.add_paragraph(f"Info: {desc}", style='List Bullet')
                bp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                bp.paragraph_format.space_after = Pt(1)
                bp.paragraph_format.keep_together = True
                bp.paragraph_format.keep_with_next = True
                if bp.runs: 
                    bp.runs[0].font.name = 'Calibri'
                    bp.runs[0].font.size = Pt(10)
            
            keywords = ", ".join(proj.get('keywords', []))
            if keywords:
                bp = doc.add_paragraph(f"Tech: {keywords}", style='List Bullet')
                bp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                bp.paragraph_format.space_after = Pt(1)
                bp.paragraph_format.keep_together = True
                bp.paragraph_format.keep_with_next = True
                if bp.runs: 
                    bp.runs[0].font.name = 'Calibri'
                    bp.runs[0].font.size = Pt(10)
            
            highlights = proj.get('highlights', [])
            if highlights:
                bp = doc.add_paragraph("Details:", style='List Bullet')
                bp.paragraph_format.space_after = Pt(1)
                bp.paragraph_format.keep_together = True
                bp.paragraph_format.keep_with_next = True
                for i, highlight in enumerate(highlights):
                    sub_bp = doc.add_paragraph(highlight)
                    sub_bp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    # Emulate indented bullet
                    sub_bp.paragraph_format.left_indent = Inches(0.5)
                    sub_bp.paragraph_format.space_after = Pt(1)
                    sub_bp.paragraph_format.keep_together = True
                    if i < len(highlights) - 1:
                        sub_bp.paragraph_format.keep_with_next = True
                    
                    # Prefix with dash
                    r_hl = sub_bp.add_run(f"- {highlight}")
                    r_hl.font.name = 'Calibri'
                    r_hl.font.size = Pt(10)
                
            doc.add_paragraph().paragraph_format.space_after = Pt(4)

    certs_items = data.get("certificates", [])
    if certs_items:
        add_heading('ZERTIFIKATE & WEITERBILDUNG')
        for cert in certs_items:
            date = cert.get('date', '')
            name = cert.get('name', '')
            issuer = cert.get('issuer', '')
            text = f"{name} - {issuer} ({date})" if date else f"{name} - {issuer}"
            bp = doc.add_paragraph(text, style='List Bullet')
            bp.paragraph_format.space_after = Pt(1)
            bp.paragraph_format.keep_together = True
            if bp.runs: 
                bp.runs[0].font.name = 'Calibri'
                bp.runs[0].font.size = Pt(10)

    langs_items = data.get("languages", [])
    if langs_items:
        add_heading('SPRACHEN')
        for lang in langs_items:
            text = f"{lang.get('language', '')}: {lang.get('fluency', '')}"
            bp = doc.add_paragraph(text, style='List Bullet')
            bp.paragraph_format.space_after = Pt(1)
            bp.paragraph_format.keep_together = True
            if bp.runs: 
                bp.runs[0].font.name = 'Calibri'
                bp.runs[0].font.size = Pt(10)

    try:
        doc.save(output_file)
        print(f"Success! {output_file} has been generated.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    generate_cv()
