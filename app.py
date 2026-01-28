import subprocess
import sys
import sqlite3
from datetime import datetime

# --- 1. AUTO-DEPENDENCY INSTALLER ---
required = ["streamlit", "requests", "beautifulsoup4", "pandas", "plotly"]
for pkg in required:
    try:
        __import__(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import urllib.parse
from urllib.parse import urljoin

# --- 2. ROBUST NAME EXTRACTION ---
def get_clean_name(url):
    """Extracts actual brand name (e.g., 'Apple' instead of 'com')"""
    clean = re.sub(r'^https?://', '', url.lower())
    clean = re.sub(r'^www\.', '', clean)
    parts = clean.split('.')
    return parts[0].capitalize() if parts else "Entity"

# --- 3. DATABASE LOGIC ---
def init_db():
    conn = sqlite3.connect('intelligence.db')
    c = conn.cursor()
    try:
        c.execute("SELECT target_name, my_name FROM history LIMIT 1")
    except sqlite3.OperationalError:
        c.execute("DROP TABLE IF EXISTS history")
        
    c.execute('''CREATE TABLE IF NOT EXISTS history 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  date TEXT, time TEXT, target_name TEXT, my_name TEXT)''')
    conn.commit()
    conn.close()

def save_to_vault(target_name, my_name):
    conn = sqlite3.connect('intelligence.db')
    c = conn.cursor()
    now = datetime.now()
    c.execute("INSERT INTO history (date, time, target_name, my_name) VALUES (?, ?, ?, ?)", 
              (now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), target_name, my_name))
    conn.commit()
    conn.close()

def get_vault_history():
    conn = sqlite3.connect('intelligence.db')
    df = pd.read_sql_query("SELECT date as 'Date', time as 'Time', target_name as 'Target', my_name as 'Me' FROM history ORDER BY id DESC", conn)
    conn.close()
    return df

init_db()

# --- 4. NOIR ELITE DESIGN SYSTEM (FORCED CONTRAST) ---
st.set_page_config(page_title="Mr.BDE Pro", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    
    /* GLOBAL THEME */
    .stApp { background-color: #000000 !important; font-family: 'Inter', sans-serif; }
    h1, h2, h3, h4, p, label, span, div, .stMarkdown { color: #FFFFFF; }

    /* KPI GRID */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-bottom: 40px;
    }
    .kpi-card {
        background-color: #000000 !important;
        padding: 30px;
        text-align: center;
        border-radius: 4px;
        border: 1px solid #FFFFFF !important;
    }
    .kpi-card h4 { 
        color: #888888 !important; 
        font-size: 0.8rem !important; 
        font-weight: 700 !important; 
        text-transform: uppercase; 
        letter-spacing: 2px; 
        margin: 0 0 10px 0 !important;
    }
    .kpi-card h2 { 
        color: #FFFFFF !important; 
        font-size: 1.8rem !important; 
        font-weight: 900 !important; 
        margin: 0 !important;
    }

    /* SUBMIT BUTTON */
    div.stButton > button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-weight: 900 !important;
        border-radius: 4px !important;
        width: 100% !important;
        border: none !important;
        padding: 25px !important;
        text-transform: uppercase !important;
        letter-spacing: 4px !important;
        font-size: 1.2rem !important;
    }
    
    div.stButton > button p { color: #000000 !important; font-weight: 900 !important; }
    div.stButton > button:hover { background-color: #DDDDDD !important; }

    /* WHITE MODULES */
    .white-module {
        background-color: #FFFFFF !important;
        padding: 45px;
        border-radius: 4px;
        margin-bottom: 35px;
    }
    .white-module h1, .white-module h2, .white-module h3, .white-module h4, 
    .white-module p, .white-module li, .white-module span, 
    .white-module div, .white-module b, .white-module label, .white-module strong {
        color: #000000 !important;
    }
    .module-title {
        font-size: 1.8rem; font-weight: 900; text-transform: uppercase;
        border-bottom: 4px solid #000000; padding-bottom: 10px;
        margin-bottom: 25px; color: #000000 !important;
    }

    /* INPUTS */
    .stTextInput>div>div>input { background-color: #000000 !important; color: #FFFFFF !important; border: 1px solid #FFFFFF !important; }
    
    /* SCRIPT BLOCKS */
    .script-block {
        background-color: #F5F5F5;
        border: 1px solid #000000;
        padding: 25px;
        font-family: 'Courier New', monospace;
        color: #000000 !important;
        font-weight: 600;
        margin-top: 15px;
    }

    [data-testid="stSidebar"] { background-color: #111111 !important; color: white !important; }
    .block-container { max-width: 1250px; padding-top: 3rem; margin: auto; }
    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 5. INTELLIGENCE ENGINE (ALIGNMENT MATRIX LOGIC) ---
class TitanIntelligence:
    def __init__(self, target_url, my_url):
        self.target_url = target_url if target_url.startswith("http") else f"https://{target_url}"
        self.my_url = my_url if my_url.startswith("http") else f"https://{my_url}"
        self.headers = {'User-Agent': 'Mozilla/5.0'}
        
        # THE ALIGNMENT MATRIX: Maps Tech to Pain Points and My Matching Keywords
        self.ALIGNMENT_MATRIX = {
            "Salesforce": {"pain": "CRM Adoption Fatigue", "match_keys": ["crm", "salesforce", "sales ops", "pipeline"]},
            "AWS": {"pain": "Cloud Cost Leakage", "match_keys": ["cloud", "aws", "infrastructure", "devops", "optimization"]},
            "HubSpot": {"pain": "Inbound Pipeline Friction", "match_keys": ["marketing automation", "hubspot", "lead gen", "inbound"]},
            "Zendesk": {"pain": "Customer Experience Lag", "match_keys": ["customer success", "support", "helpdesk", "cx"]},
            "Shopify": {"pain": "E-commerce Conversion Drop", "match_keys": ["e-commerce", "shopify", "retail", "online store"]},
            "WordPress": {"pain": "CMS Performance Bloat", "match_keys": ["web development", "modernization", "security", "wordpress"]},
            "Oracle": {"pain": "Legacy Database Rigidity", "match_keys": ["database", "data engineering", "migration", "analytics"]},
            "SAP": {"pain": "ERP Process Fragmentation", "match_keys": ["erp", "sap", "automation", "process audit"]},
            "ServiceNow": {"pain": "ITSM Service Silos", "match_keys": ["itsm", "servicenow", "workflow automation"]}
        }

    def fetch(self, url):
        try:
            res = requests.get(url, headers=self.headers, timeout=12)
            soup = BeautifulSoup(res.text, 'html.parser')
            return {"html": res.text.lower(), "text": soup.get_text().lower(), "soup": soup}
        except: return None

    def analyze(self):
        t_data = self.fetch(self.target_url)
        m_data = self.fetch(self.my_url)
        if not t_data or not m_data: return None

        t_name = get_clean_name(self.target_url)
        m_name = get_clean_name(self.my_url)

        # 1. Identify Tech on Target
        found_techs = [tech for tech in self.ALIGNMENT_MATRIX.keys() if tech.lower() in t_data['html']]
        
        # 2. Logic: Pick Primary Trigger and Match with My Site
        trigger_tech = "General Infrastructure"
        primary_pain = "Operational Inefficiency"
        matched_service = "Strategic Modernization"

        for tech in found_techs:
            # Check if my site mentions keywords related to this tech's pain solution
            matrix_entry = self.ALIGNMENT_MATRIX[tech]
            if any(key in m_data['text'] for key in matrix_entry['match_keys']):
                trigger_tech = tech
                primary_pain = matrix_entry['pain']
                # Pick the first keyword found on my site as the matched service
                for key in matrix_entry['match_keys']:
                    if key in m_data['text']:
                        matched_service = key.title()
                        break
                break # Stop at first strong match

        # 3. Scrape Target Careers (Firmographics)
        career_text = ""
        for a in t_data['soup'].find_all('a', href=True):
            if any(x in a['href'].lower() for x in ['career', 'job']):
                c_res = self.fetch(urljoin(self.target_url, a['href']))
                if c_res: career_text = c_res['text']
                break

        return {
            "target": {
                "name": t_name,
                "industry": "High-Tech / SaaS" if "platform" in t_data['text'] else "Commercial Services",
                "tech": found_techs,
                "trigger_tech": trigger_tech,
                "pain_point": primary_pain,
                "hiring": "Growth-Active" if len(career_text) > 1000 else "Stable"
            },
            "me": {
                "name": m_name, 
                "matched_service": matched_service
            }
        }

# --- 6. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>🛡️ ADMIN VAULT</h2>", unsafe_allow_html=True)
    admin_pw = st.text_input("Vault Access Key", type="password")
    if admin_pw == "Sibin@8129110807":
        st.success("Authorized")
        st.dataframe(get_vault_history())
    elif admin_pw != "": st.error("Access Denied")

# --- 7. FRONTEND DASHBOARD ---
st.markdown("<h1 style='text-align:center; letter-spacing:15px; font-weight:900;'>Mr.BDE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#666666;'>Developed by Sibin Kalliyath | Version 3.0</p>", unsafe_allow_html=True)

col_a, col_b = st.columns(2)
with col_a: t_in = st.text_input("TARGET URL (PROSPECT)", placeholder="e.g. apple.com")
with col_b: m_in = st.text_input("YOUR COMPANY URL (VENDOR)", placeholder="e.g. salesforce.com")

if st.button("Initiate Strategic Audit"):
    engine = TitanIntelligence(t_in, m_in)
    with st.spinner("EXECUTING ALIGNMENT MATRIX SCAN..."):
        data = engine.analyze()
        if data: save_to_vault(data['target']['name'], data['me']['name'])
    
    if data:
        # --- KPI GRID ---
        st.markdown(f"""
            <div class="kpi-grid">
                <div class="kpi-card"><h4>Lead Status</h4><h2>High Priority</h2></div>
                <div class="kpi-card"><h4>Trigger Tech</h4><h2>{data['target']['trigger_tech']}</h2></div>
                <div class="kpi-card"><h4>Primary Pain</h4><h2>{data['target']['pain_point']}</h2></div>
                <div class="kpi-card"><h4>Match Strength</h4><h2>Strong</h2></div>
            </div>
        """, unsafe_allow_html=True)

        # --- MODULE 1: STRATEGIC BRIDGE ---
        st.markdown(f"""
            <div class="white-module">
                <div class="module-title">Alignment Summary: {data['me']['name']} → {data['target']['name']}</div>
                <p><b>Executive Observation:</b> We detected <b>{data['target']['trigger_tech']}</b> on the prospect's site, which typically correlates with <b>{data['target']['pain_point']}</b>.</p>
                <p><b>Solution Fit:</b> Your site explicitly mentions <b>{data['me']['matched_service']}</b>, creating a direct competitive advantage for this account.</p>
            </div>
        """, unsafe_allow_html=True)

        # --- MODULE 2: TARGET PROFILE ---
        st.markdown('<div class="white-module">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">Target Intelligence Profile</div>', unsafe_allow_html=True)
        p1, p2 = st.columns(2)
        with p1:
            st.write(f"**Entity Name:** {data['target']['name']}")
            st.write(f"**Sector:** {data['target']['industry']}")
            st.write(f"**Hiring Posture:** {data['target']['hiring']}")
        with p2:
            st.write("**Identified Stack:** " + (", ".join(data['target']['tech']) if data['target']['tech'] else "Custom Systems"))
            st.write(f"**Pain Point identified:** {data['target']['pain_point']}")
        st.markdown('</div>', unsafe_allow_html=True)

        # --- MODULE 3: LINKEDIN STAKEHOLDER RADAR ---
        st.markdown('<div class="white-module">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">LinkedIn Stakeholder Radar</div>', unsafe_allow_html=True)
        roles = ["CTO", "VP Operations", "Head of Digital Transformation", "Sales Director"]
        r_cols = st.columns(4)
        for i, r in enumerate(roles):
            with r_cols[i]:
                st.write(f"**{r}**")
                q = urllib.parse.quote(f"{data['target']['name']} {r}")
                st.markdown(f'<a href="https://www.linkedin.com/search/results/people/?keywords={q}" target="_blank" style="color:blue!important; text-decoration:underline; font-weight:bold;">🔍 Search LinkedIn</a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # --- MODULE 4: SALES PLAYBOOK (DYNAMIC SCRIPTS) ---
        st.markdown('<div class="white-module">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">Sales Execution Playbook</div>', unsafe_allow_html=True)
        
        st.write("**📧 High-Impact Email Script**")
        st.markdown(f"""<div class="script-block">
        Subject: Question regarding {data['target']['name']}'s {data['target']['trigger_tech']} ecosystem<br><br>
        "Hi [Name], I noticed {data['target']['name']} is currently leveraging <b>{data['target']['trigger_tech']}</b> as part of your digital roadmap.<br><br>
        Usually, firms at your scale experience <b>{data['target']['pain_point']}</b> when managing these systems. <br><br>
        At <b>{data['me']['name']}</b>, we specialize in <b>{data['me']['matched_service']}</b> to eliminate this specific friction. Do you have 2 minutes Tuesday?"
        </div>""", unsafe_allow_html=True)
        
        st.write("**☎️ Tele-Calling Script**")
        st.markdown(f"""<div class="script-block">
        "Hi [Name], it's [YourName] from {data['me']['name']}. I noticed you're using <b>{data['target']['trigger_tech']}</b> and are currently in a <b>{data['target']['hiring']}</b> phase. 
        Most VPs I talk to say their biggest hurdle with that stack is <b>{data['target']['pain_point']}</b>. We've solved this—do you have a moment?"
        </div>""", unsafe_allow_html=True)

        st.write("**📟 Voicemail Hook**")
        st.markdown(f"""<div class="script-block">
        "Hi [Name], I have a specific insight regarding {data['target']['name']}'s <b>{data['target']['trigger_tech']}</b> setup and how to solve the <b>{data['target']['pain_point']}</b> many firms face. <br><br>
        I'll follow up with an email under the subject: <b>{data['target']['name']} Strategy</b>."
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    else: st.error("Audit failed. Ensure URLs are valid.")
