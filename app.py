import streamlit as st
import os
import json
import time
import uuid
import concurrent.futures
import text_analyzer
import cv_generator
import cover_letter_generator
import combined_generator
import file_utils
import version
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI CV & Cover Letter Generator", page_icon="📄", layout="wide")
os.makedirs("output", exist_ok=True)

st.title("📄 AI CV & Cover Letter Generator")
st.markdown("Generate professional, ATS-friendly CVs and Cover Letters using Artificial Intelligence.")

# --- SIDEBAR ---
st.sidebar.header("⚙️ Settings")
api_provider = st.sidebar.radio("Select AI Provider:", ["OpenAI", "Google Gemini"])

api_key = ""
if api_provider == "OpenAI":
    api_key = st.sidebar.text_input("OpenAI API Key (sk-...):", type="password", value=os.environ.get("OPENAI_API_KEY", ""))
else:
    api_key = st.sidebar.text_input("Gemini API Key:", type="password", value=os.environ.get("GEMINI_API_KEY", ""))

st.sidebar.markdown("---")
target_language = st.sidebar.radio("🌐 AI Output Language:", ["Deutsch (German)", "English"])
st.sidebar.markdown("---")
st.sidebar.caption(f"🚀 Version: **{version.VERSION}**")
st.sidebar.caption(f"📅 Last Update: {version.LAST_UPDATED}")
st.sidebar.caption("Made with ❤️ in 2026")

# Cleanup old persistent files from disk to ensure privacy/no-caching (as requested)
for f in ["data.json", "cover_letter.json", "output/profile.jpg"]:
    if os.path.exists(f):
        try: os.remove(f)
        except: pass

# --- TABS ---
tabs_list = [
    "🔍 1. Extraction", 
    "✍️ 2. CV Editor", 
    "✉️ 3. Cover Letter", 
    "💾 4. Export & Download"
]

st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Private Area")
private_password = st.sidebar.text_input("Amjad's Password:", type="password")
if private_password == "amjad" or private_password == "amjad123":
    tabs_list.append("💎 5. Amjad's Private CV")

tab_objects = st.tabs(tabs_list)
tab1 = tab_objects[0]
tab2 = tab_objects[1]
tab3 = tab_objects[2]
tab4 = tab_objects[3]
tab5 = tab_objects[4] if len(tab_objects) > 4 else None

def run_with_animation(task_func, task_type="extract", lang="German"):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    is_en = "english" in lang.lower()
    
    if task_type == "extract":
         if is_en:
             steps = [
                (10, "Initializing AI connection..."),
                (25, "Reading and cleaning raw data..."),
                (45, "Analyzing career path and structuring experience..."),
                (60, "Applying C2-Level grammar and orthography checks..."),
                (75, "Applying improvements and requested fixes..."),
                (85, "Formatting JSON Resume data..."),
                (95, "Finalizing data processing...")
             ]
         else:
             steps = [
                (10, "Initializiere Verbindung zur KI..."),
                (25, "Lese und bereinige Rohdaten..."),
                (45, "Analysiere Laufbahn und Strukturieren der Erfahrungen..."),
                (60, "Prüfe Grammatik und Orthografie (C2-Level)..."),
                (75, "Wende Verbesserungen und Fixes an..."),
                (85, "Formatiere JSON Resume Daten..."),
                (95, "Finalisiere Datenverarbeitung...")
             ]
    else:
         if is_en:
             steps = [
                (15, "Transmitting data securely to HR Agent..."),
                (35, "Evaluating structure and professional impact..."),
                (55, "Analyzing strengths and weaknesses..."),
                (75, "Generating concrete improvement suggestions..."),
                (90, "Finalizing HR report...")
             ]
         else:
             steps = [
                (15, "Übertrage Daten sicher an HR-Agenten..."),
                (35, "Bewerte Struktur und professionelle Wirkung..."),
                (55, "Analysiere Stärken und Auffälligkeiten..."),
                (75, "Erstelle Punkte für Verbesserungen..."),
                (90, "Finalisiere Bericht...")
             ]
         
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(task_func)
        step_idx = 0
        while not future.done():
            if step_idx < len(steps):
                pct, msg = steps[step_idx]
                progress_bar.progress(pct)
                status_text.markdown(f"**⏳ {msg} ({pct}%)**")
                step_idx += 1
            time.sleep(0.8)
            
        progress_bar.progress(100)
        success_msg = "✅ Process successfully completed (100%)!" if is_en else "✅ Vorgang erfolgreich abgeschlossen (100%)!"
        status_text.markdown(f"**{success_msg}**")
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
        return future.result()

# --- TAB 1: EXTRACTION ---
with tab1:
    st.header("Extract Data from Original CV")
    col1, col2 = st.columns([1.5, 1])
    with col1:
        st.subheader("Option A: Upload CV File")
        uploaded_cv = st.file_uploader("Upload your existing CV (PDF, DOCX, TXT):", type=['pdf', 'docx', 'txt'])
        
        st.subheader("Option B: Paste Text Manually")
        raw_cv_text = st.text_area("Or paste your unstructured CV / LinkedIn text here:", height=200)

        # Trigger extraction from file if uploaded
        if uploaded_cv:
            with st.spinner("Extracting text from file..."):
                extracted_file_text = file_utils.extract_text_from_file(uploaded_cv)
                if not extracted_file_text.startswith("Error") and extracted_file_text != "Unsupported file format.":
                    raw_cv_text = extracted_file_text
                    st.success(f"Successfully extracted text from {uploaded_cv.name}!")
                else:
                    st.error(extracted_file_text)
    with col2:
        st.info("💡 **Tip:** Uploading your old CV is the fastest way to start. The AI will understand the structure automatically.")

    st.markdown("---")
    st.subheader("⚡ Step 1: Evaluate your Profile (Optional)")
    st.caption("Get professional HR feedback and identify weaknesses before generating your final CV.")
    
    if st.button("⭐ Request HR-Feedback", use_container_width=True):
        if not api_key:
            st.error("Please enter an API Key in the sidebar.")
        elif not raw_cv_text.strip():
            st.error("Please insert raw text to evaluate.")
        else:
            provider = 'openai' if api_provider == "OpenAI" else 'gemini'
            try:
                rating = run_with_animation(
                    lambda: text_analyzer.rate_cv(raw_cv_text, api_key, provider=provider, target_language=target_language),
                    task_type="rate",
                    lang=target_language
                )
                st.session_state['hr_rating'] = rating
            except Exception as e:
                st.error(f"❌ API Error: {str(e)}")

    if 'hr_rating' in st.session_state:
        rating = st.session_state['hr_rating']
        if isinstance(rating, dict):
            st.metric("HR Score", rating.get("score", "N/A"))
            st.success("💪 Strengths:\n" + "\n".join([f"- {s}" for s in rating.get("strengths", [])]))
            st.warning("⚠️ Weaknesses:\n" + "\n".join([f"- {w}" for w in rating.get("weaknesses", [])]))
            st.session_state['hr_weaknesses'] = rating.get("weaknesses", [])
        else:
            st.info(str(rating))

    st.markdown("---")
    st.subheader("🚀 Step 2: Extract & Auto-Improve")
    st.caption("The AI will extract your data structurally and automatically fix any selected weaknesses.")

    custom_improvements = []
    if 'hr_weaknesses' in st.session_state and st.session_state['hr_weaknesses']:
        st.markdown("### 🛠️ Weakness Auto-Fixer")
        custom_improvements = st.multiselect(
            "Select the weaknesses you want the AI to automatically fix during extraction:",
            options=st.session_state['hr_weaknesses'],
            default=st.session_state['hr_weaknesses']
        )

    if st.button("✨ Extract CV & Apply Improvements", type="primary", use_container_width=True):
        if not api_key:
            st.error("Please enter an API Key in the sidebar.")
        elif not raw_cv_text.strip():
            st.error("Please insert raw text to extract.")
        else:
            provider = 'openai' if api_provider == "OpenAI" else 'gemini'
            try:
                extracted_data = run_with_animation(
                    lambda: text_analyzer.analyze_cv_text(raw_cv_text, api_key, provider=provider, target_language=target_language, custom_improvements=custom_improvements),
                    task_type="extract",
                    lang=target_language
                )
                
                if extracted_data:
                    st.success("Data successfully extracted! Go to Tab 2 to review and edit.")
                    st.session_state['cv_data'] = extracted_data
                    if 'hr_rating' in st.session_state: del st.session_state['hr_rating']
                    if 'hr_weaknesses' in st.session_state: del st.session_state['hr_weaknesses']
                else:
                    st.error("Error during extraction. No data returned.")
            except Exception as e:
                st.error(f"❌ API Error: {str(e)}")


# --- TAB 2: EDITOR ---
with tab2:
    st.header("Interactive CV Editor")
    if 'cv_data' not in st.session_state:
        st.warning("No CV data extracted yet. Please go to Tab 1 and extract your data first.")
    else:
        cv = st.session_state['cv_data']
        
        st.markdown("### Profile Picture (Bewerbungsfoto)")
        uploaded_file = st.file_uploader("Upload a professional photo (JPG/PNG) to include in your CV header:", type=['jpg', 'jpeg', 'png'])
        
        col_img1, col_img2 = st.columns([1, 1])
        with col_img1:
            if uploaded_file is not None:
                # Store photo as bytes in session_state instead of on disk
                st.session_state['photo_bytes'] = uploaded_file.getvalue()
                # Update cv_data to include photo reference (bytes)
                if 'cv_data' in st.session_state:
                    st.session_state['cv_data']['basics']['photo'] = st.session_state['photo_bytes']
                st.success("✅ Profile picture uploaded to session!")
            
            if 'photo_bytes' in st.session_state:
                if st.button("🗑️ Remove Profile Picture"):
                    if 'photo_bytes' in st.session_state: del st.session_state['photo_bytes']
                    if 'cv_data' in st.session_state and 'photo' in st.session_state['cv_data']['basics']:
                        del st.session_state['cv_data']['basics']['photo']
                    st.rerun()
        with col_img2:
            if 'photo_bytes' in st.session_state:
                import base64
                img_b64 = base64.b64encode(st.session_state['photo_bytes']).decode()
                st.markdown(f'<img src="data:image/jpeg;base64,{img_b64}" width="100" style="border-radius: 5px;">', unsafe_allow_html=True)
                st.caption("Current Photo")
        
        st.markdown("### Basics")
        basics = cv.get('basics', {})
        c1, c2 = st.columns(2)
        with c1:
            basics['name'] = st.text_input("Full Name", basics.get('name', ''))
            basics['label'] = st.text_input("Job Title / Profession", basics.get('label', ''))
            basics['email'] = st.text_input("Email", basics.get('email', ''))
        with c2:
            basics['phone'] = st.text_input("Phone", basics.get('phone', ''))
            loc = basics.get('location', {})
            if isinstance(loc, str):
                loc = {'city': loc, 'postalCode': ''}
            elif not isinstance(loc, dict):
                loc = {}
            loc['city'] = st.text_input("City", loc.get('city', ''))
            loc['postalCode'] = st.text_input("Postal Code", loc.get('postalCode', ''))
            basics['location'] = loc
            
        basics['summary'] = st.text_area("Professional Summary", basics.get('summary', ''), height=150)
        cv['basics'] = basics
        
        st.markdown("### Work Experience")
        for i, work in enumerate(cv.get('work', [])):
            with st.expander(f"Work: {work.get('position', 'Role')} at {work.get('name', 'Company')}"):
                w1, w2 = st.columns(2)
                with w1:
                    work['position'] = st.text_input(f"Position", work.get('position', ''), key=f"w_pos_{i}")
                    work['name'] = st.text_input(f"Company", work.get('name', ''), key=f"w_name_{i}")
                with w2:
                    work['startDate'] = st.text_input(f"Start Date", work.get('startDate', ''), key=f"w_start_{i}")
                    work['endDate'] = st.text_input(f"End Date", work.get('endDate', ''), key=f"w_end_{i}")
                
                bullets_str = "\n".join(work.get('highlights', []))
                edited_bullets = st.text_area(f"Highlights/Bullet points (one per line)", bullets_str, height=100, key=f"w_bull_{i}")
                work['highlights'] = [b.strip() for b in edited_bullets.split('\n') if b.strip()]
        
        st.markdown("### Education")
        for i, edu in enumerate(cv.get('education', [])):
            with st.expander(f"Edu: {edu.get('area', 'Degree')} at {edu.get('institution', 'Institution')}"):
                 e1, e2 = st.columns(2)
                 with e1:
                     edu['area'] = st.text_input(f"Degree/Area", edu.get('area', ''), key=f"e_area_{i}")
                     edu['institution'] = st.text_input(f"Institution", edu.get('institution', ''), key=f"e_inst_{i}")
                 with e2:
                     edu['startDate'] = st.text_input(f"Edu Start", edu.get('startDate', ''), key=f"e_start_{i}")
                     edu['endDate'] = st.text_input(f"Edu End", edu.get('endDate', ''), key=f"e_end_{i}")

        st.markdown("### Projects")
        for i, proj in enumerate(cv.get('projects', [])):
            with st.expander(f"Project: {proj.get('name', 'Name')}"):
                p1, p2 = st.columns([1, 1])
                with p1:
                    proj['name'] = st.text_input("Project Name", proj.get('name', ''), key=f"p_name_{i}")
                with p2:
                    proj['url'] = st.text_input("Project URL/Link", proj.get('url', ''), key=f"p_url_{i}")
                
                proj['description'] = st.text_area("Short Description", proj.get('description', ''), height=70, key=f"p_desc_{i}")
                
                bullets_str = "\n".join(proj.get('highlights', []))
                edited_bullets = st.text_area("Highlights/Bullet points (one per line)", bullets_str, height=100, key=f"p_bull_{i}")
                proj['highlights'] = [b.strip() for b in edited_bullets.split('\n') if b.strip()]
        
        st.markdown("### Skills")
        for i, skill in enumerate(cv.get('skills', [])):
             s_col1, s_col2 = st.columns([1, 2])
             with s_col1:
                 skill['name'] = st.text_input(f"Skill Category", skill.get('name', ''), key=f"s_name_{i}")
             with s_col2:
                 kw = ", ".join(skill.get('keywords', []))
                 edited_kw = st.text_input(f"Keywords (comma separated)", kw, key=f"s_kw_{i}")
                 skill['keywords'] = [k.strip() for k in edited_kw.split(',')]
                 
        if st.button("💾 Save CV Changes", use_container_width=True):
             # Save directly to session state
             st.session_state['cv_data'] = cv
             st.success("Changes saved for this session! You can now export the CV.")


# --- TAB 3: COVER LETTER ---
with tab3:
    st.header("Cover Letter Generation")
    st.markdown("Generate a tailored cover letter using AI, or paste your own to format it identically to your CV.")
    
    col_c1, col_c2 = st.columns([1, 1])
    with col_c1:
        job_description = st.text_area("Paste the Job Description here (if using AI):", height=200)
    with col_c2:
        if st.button("✉️ AI Generate Cover Letter Data", use_container_width=True):
             if 'cv_data' not in st.session_state:
                 st.error("Please extract your CV data in Tab 1 first.")
             elif not job_description.strip():
                 st.warning("Please provide a Job Description.")
             elif not api_key:
                 st.error("API Key is missing.")
             else:
                 with st.spinner("Analyzing match and writing tailored cover letter..."):
                     provider = 'openai' if api_provider == "OpenAI" else 'gemini'
                     try:
                        cl_data = text_analyzer.generate_cover_letter_data(st.session_state['cv_data'], job_description, api_key, provider=provider, target_language=target_language)
                        
                        if cl_data:
                            st.success("Cover letter content generated! You can edit it below.")
                            st.session_state['cl_data'] = cl_data
                        else:
                            st.error("Error during generation. No data returned.")
                     except Exception as e:
                        st.error(f"❌ API Error: {str(e)}")
                         
        st.markdown("🔹 **OR**")
        
        if st.button("✍️ Paste My Own Cover Letter Manually", use_container_width=True):
             dummy_cl = {
                 "recipient": {"company": "Company Name", "contact_person": "Contact Person", "address": "Street 123", "postal_code": "12345", "city": "City"},
                 "location": "My City",
                 "subject": "Bewerbung als [Position]",
                 "salutation": "Sehr geehrte(r) Herr/Frau [Name],",
                 "paragraphs": ["Paste your first paragraph here...", "Paste your second paragraph here..."],
                 "closing": "Mit freundlichen Grüßen"
             }
             st.session_state['cl_data'] = dummy_cl
             st.success("Manual mode activated! Edit the fields below.")

    if 'cl_data' in st.session_state:
         st.markdown("---")
         st.subheader("Cover Letter Editor")
         cl = st.session_state['cl_data']
         
         # Allow editing recipient data as well
         r1, r2, r3 = st.columns(3)
         rec = cl.get('recipient', {})
         with r1:
             rec['company'] = st.text_input("Company", rec.get('company', ''), key="cl_company")
             rec['postal_code'] = st.text_input("Postal Code", rec.get('postal_code', ''), key="cl_postal_code")
         with r2:
             rec['contact_person'] = st.text_input("Contact Person", rec.get('contact_person', ''), key="cl_contact_person")
             rec['city'] = st.text_input("City", rec.get('city', ''), key="cl_city")
         with r3:
             rec['address'] = st.text_input("Street / Address", rec.get('address', ''), key="cl_address")
             cl['location'] = st.text_input("My Location (Date)", cl.get('location', ''), key="cl_my_location")
         
         cl['recipient'] = rec
         
         c1, c2 = st.columns(2)
         with c1: cl['subject'] = st.text_input("Subject", cl.get('subject', ''))
         with c2: cl['salutation'] = st.text_input("Salutation", cl.get('salutation', ''))
         
         cl_body = "\n\n".join(cl.get('paragraphs', []))
         edited_body = st.text_area("Body Paragraphs (separated by double newlines)", cl_body, height=250)
         cl['paragraphs'] = [p.strip() for p in edited_body.split('\n\n') if p.strip()]
         
         if st.button("💾 Save Cover Letter Edits", use_container_width=True):
             st.session_state['cl_data'] = cl
             st.success("Cover letter edits saved for this session! You can now export it.")

# --- TAB 4: EXPORT ---
with tab4:
    st.header("Export Documents")
    
    cv_ready = 'cv_data' in st.session_state
    cl_ready = 'cl_data' in st.session_state
    
    export_c1, export_c2, export_c3 = st.columns(3)
    
    with export_c1:
        st.subheader("📄 1. Standalone CV")
        if not cv_ready:
            st.warning("Extract your CV data first (Tab 1).")
        else:
            if st.button("Generate CV Document", use_container_width=True):
                 with st.spinner("Building Docx..."):
                     ts = time.strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]
                     fname = f"output/Resume_{ts}.docx"
                     cv_generator.generate_cv(st.session_state['cv_data'], fname)
                     st.session_state['out_cv'] = fname
                     st.success("Generated successfully!")
            if 'out_cv' in st.session_state:
                 path = st.session_state['out_cv']
                 with open(path, "rb") as f:
                      st.download_button("⬇️ Download CV", data=f, file_name=os.path.basename(path), mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
                 if st.button("📂 Open CV File", use_container_width=True, key="open_cv"):
                     os.startfile(os.path.abspath(path))

    with export_c2:
        st.subheader("✉️ 2. Cover Letter")
        if not cl_ready:
            st.warning("Generate your Cover Letter first (Tab 3).")
        else:
            if st.button("Generate Cover Letter", use_container_width=True):
                 with st.spinner("Building Docx..."):
                     ts = time.strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]
                     fname = f"output/CoverLetter_{ts}.docx"
                     cover_letter_generator.generate_cover_letter(st.session_state['cv_data'], st.session_state['cl_data'], fname)
                     st.session_state['out_cl'] = fname
                     st.success("Generated successfully!")
            if 'out_cl' in st.session_state:
                 path = st.session_state['out_cl']
                 with open(path, "rb") as f:
                      st.download_button("⬇️ Download Cover Letter", data=f, file_name=os.path.basename(path), mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
                 if st.button("📂 Open Cover Letter", use_container_width=True, key="open_cl"):
                     os.startfile(os.path.abspath(path))

    with export_c3:
        st.subheader("📥 3. Combined Application")
        if not (cv_ready and cl_ready):
             st.warning("Both CV and Cover Letter must be generated.")
        else:
            if st.button("Generate Combined Doc", use_container_width=True):
                  with st.spinner("Building Docx..."):
                      ts = time.strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]
                      fname = f"output/Application_{ts}.docx"
                      combined_generator.generate_combined(st.session_state['cv_data'], st.session_state['cl_data'], fname)
                      st.session_state['out_combo'] = fname
                      st.success("Generated successfully!")
            if 'out_combo' in st.session_state:
                 path = st.session_state['out_combo']
                 with open(path, "rb") as f:
                      st.download_button("⬇️ Download Application", data=f, file_name=os.path.basename(path), mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
                 if st.button("📂 Open Application", use_container_width=True, key="open_combo"):
                     os.startfile(os.path.abspath(path))

# --- TAB 5: PRIVATE CV ---
if tab5:
    with tab5:
        st.header("💎 Amjad's Private CV: Faithful Translation & Rebuilding")
        st.markdown("This area is optimized to **rebuild your CV in a new language** while strictly preserving your original structure, links, and formatting style.")
        
        target_lang_private = st.radio("Select Target Language:", ["Deutsch (German)", "English"], key="private_lang")
        
        st.markdown("---")
        
        # Determine master CV text
        current_dir = os.path.dirname(os.path.abspath(__file__))
        local_path = os.path.join(current_dir, "private", "Amjad_CV.docx")
        
        master_cv_text = ""
        if os.path.exists(local_path):
            st.info("✅ Master CV detected in the system.")
            import file_utils
            master_cv_text = file_utils.extract_text_with_links_from_local(local_path)
        else:
            st.warning("⚠️ Master CV not found. Please upload it to begin.")
            uploaded_master = st.file_uploader("Upload Master CV (DOCX):", type=['docx'], key="master_uploader")
            if uploaded_master:
                import file_utils
                master_cv_text = file_utils.extract_text_from_file(uploaded_master)
                st.success("Master CV loaded for this session.")

        if st.button("🚀 Rebuild CV in " + target_lang_private, type="primary", use_container_width=True):
            if not api_key:
                st.error("Please enter an API Key in the sidebar.")
            elif not master_cv_text:
                st.error("Please provide your Master CV first.")
            else:
                with st.spinner("Translating while preserving structure & links..."):
                    provider = 'openai' if api_provider == "OpenAI" else 'gemini'
                    try:
                        import text_analyzer
                        extracted_data = run_with_animation(
                            lambda: text_analyzer.translate_cv_faithfully(master_cv_text, target_lang_private, api_key, provider=provider),
                            task_type="extract",
                            lang=target_lang_private
                        )
                        
                        if extracted_data:
                            st.session_state['cv_data'] = extracted_data
                            st.success(f"✅ CV Successfully Rebuilt in {target_lang_private}!")
                            
                            import time, uuid, os, cv_generator
                            ts = time.strftime("%Y%m%d_%H%M%S")
                            fname = f"output/Amjad_Faithful_CV_{'DE' if 'Deutsch' in target_lang_private else 'EN'}_{ts}.docx"
                            cv_generator.generate_cv(extracted_data, fname)
                            
                            with open(fname, "rb") as f:
                                st.download_button("⬇️ Download Rebuilt CV", data=f, file_name=os.path.basename(fname), mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
                        else:
                            st.error("Translation failed.")
                    except Exception as e:
                        st.error(f"❌ API Error: {str(e)}")
