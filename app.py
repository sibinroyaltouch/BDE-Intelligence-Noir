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

# --- 3. DATABASE LOGIC (WITH AUTO-SCHEMA REPAIR) ---
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
st.set_page_config(page_title="Mr. BDE Pro", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    
    /* GLOBAL THEME */
    .stApp { background-color: #000000 !important; font-family: 'Inter', sans-serif; }
    h1, h2, h3, h4, p, label, span, div, .stMarkdown { color: #FFFFFF; }

    /* KPI GRID: BLACK BACKGROUND AND WHITE TEXT (REQUESTED CHANGE) */
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
        border: 1px solid #FFFFFF !important; /* White border to define the black box */
    }
    .kpi-card h4 { 
        color: #888888 !important; /* Dimmed label */
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

    /* SUBMIT BUTTON: WHITE BACKGROUND AND BOLD BLACK TEXT (REQUESTED) */
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
    
    /* Ensure the button text stays black on all systems */
    div.stButton > button p {
        color: #000000 !important;
        font-weight: 900 !important;
    }
    div.stButton > button:hover { background-color: #DDDDDD !important; }

    /* WHITE MODULES: KEEPING BLACK TEXT FOR DOSSIER MODULES */
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

    /* INPUT FIELD STYLING */
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

# --- 5. INTELLIGENCE ENGINE ---
class TitanIntelligence:
    def __init__(self, target_url, my_url):
        self.target_url = target_url if target_url.startswith("http") else f"https://{target_url}"
        self.my_url = my_url if my_url.startswith("http") else f"https://{my_url}"
        self.headers = {'User-Agent': 'Mozilla/5.0'}

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

        # Tech Identification
        tech_list = ["Salesforce", "AWS", "HubSpot", "Zendesk", "Shopify", "WordPress", "Oracle", "SAP", "ServiceNow"]
        found_tech = [x for x in tech_list if x.lower() in t_data['html']]
        
        # Self-Service Logic
        my_offer_keys = {"Cloud Engineering": ["aws", "cloud", "devops"], "AI/Automation": ["ai", "machine", "automation"], "Cybersecurity": ["security", "soc"], "CRM Acceleration": ["salesforce", "hubspot"]}
        my_strengths = [k for k, v in my_offer_keys.items() if any(x in m_data['text'] for x in v)]
        
        return {
            "target": {
                "name": t_name,
                "industry": "High-Tech / SaaS" if "platform" in t_data['text'] else "Commercial Services",
                "tech": found_tech,
                "hiring": "Growth-Active" if "career" in t_data['html'] else "Stable",
                "weakness": "Operational Scale Friction"
            },
            "me": {"name": m_name, "services": my_strengths if my_strengths else ["Strategic Modernization"], "url": self.my_url}
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
st.markdown("<h1 style='text-align:center; letter-spacing:15px; font-weight:900;'>Mr. BDE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#666666;'>Developed by Sibin Kalliyath | Version 2.0</p>", unsafe_allow_html=True)

col_a, col_b = st.columns(2)
with col_a: t_in = st.text_input("TARGET URL (PROSPECT)", placeholder="e.g. apple.com")
with col_b: m_in = st.text_input("MY URL (COMPANY)", placeholder="e.g. salesforce.com")

if st.button("Initiate Strategic Audit"):
    engine = TitanIntelligence(t_in, m_in)
    with st.spinner("EXECUTING SECURE CRAWL..."):
        data = engine.analyze()
        if data: save_to_vault(data['target']['name'], data['me']['name'])
    
    if data:
        # --- KPI GRID (BLACK BACKGROUND / WHITE TEXT - AS REQUESTED) ---
        st.markdown(f"""
            <div class="kpi-grid">
               <div class="kpi-card"><h4>Lead Status</h4><h2>High Priority</h2></div>
                <div class="kpi-card"><h4>Target Account</h4><h2>{data['target']['name']}</h2></div>
                <div class="kpi-card"><h4>Industry</h4><h2>{data['target']['industry']}</h2></div>
                <div class="kpi-card"><h4>Vault</h4><h2>Logged</h2></div> 
            </div>
        """, unsafe_allow_html=True)

        # --- MODULE 1: STRATEGIC BRIDGE ---
        st.markdown(f"""
            <div class="white-module">
                <div class="module-title">Strategic Bridge: {data['me']['name']} → {data['target']['name']}</div>
                <p><b>Executive Observation:</b> {data['target']['name']} is scaling during a <b>{data['target']['hiring']}</b> phase but is currently hindered by <b>{data['target']['weakness']}</b>.</p>
                <p><b>Solution Fit:</b> As <b>{data['me']['name']}</b> is an expert in <b>{data['me']['services'][0]}</b>, your strength is the direct solution to their weakness.</p>
            </div>
        """, unsafe_allow_html=True)

        # --- MODULE 2: TARGET PROFILE ---
        st.markdown('<div class="white-module">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">Target Intelligence Profile</div>', unsafe_allow_html=True)
        p1, p2 = st.columns(2)
        with p1:
            st.write(f"**Entity Name:** {data['target']['name']}")
            st.write(f"**Industry Sector:** {data['target']['industry']}")
            st.write(f"**Hiring Posture:** {data['target']['hiring']}")
        with p2:
            st.write("**Internal Tech Stack:** " + (", ".join(data['target']['tech']) if data['target']['tech'] else "Custom Infrastructure"))
            st.write(f"**Operational Gap:** {data['target']['weakness']}")
        st.markdown('</div>', unsafe_allow_html=True)

        # --- MODULE 3: LINKEDIN STAKEHOLDER RADAR ---
        st.markdown('<div class="white-module">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">LinkedIn Stakeholder Radar</div>', unsafe_allow_html=True)
        roles = ["CTO", "VP Operations", "Head of Digital Transformation", "COO"]
        r_cols = st.columns(4)
        for i, r in enumerate(roles):
            with r_cols[i]:
                st.write(f"**{r}**")
                q = urllib.parse.quote(f"{data['target']['name']} {r}")
                st.markdown(f'<a href="https://www.linkedin.com/search/results/people/?keywords={q}" target="_blank" style="color:blue!important; text-decoration:underline; font-weight:bold;">🔍 Search LinkedIn</a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # --- MODULE 4: SALES PLAYBOOK ---
        st.markdown('<div class="white-module">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">Sales Execution Playbook</div>', unsafe_allow_html=True)
        
        st.write("** Professional Email Hook**")
        st.markdown(f"""<div class="script-block">
        "Hi [Name], I noticed {data['target']['name']}'s recent scale. Usually, firms growing this fast while leveraging legacy tools hit a bottleneck with <b>{data['target']['weakness']}</b>. <br><br>
        At <b>{data['me']['name']}</b>, we've helped similar firms bridge this specific gap with our <b>{data['me']['services'][0]}</b> suite. Do you have 2 minutes Tuesday?"
        </div>""", unsafe_allow_html=True)
        
        st.write("** Tele-Calling Script**")
        st.markdown(f"""<div class="script-block">
        "Hi [Name], it's [YourName] from {data['me']['name']}. I noticed you're scaling your team. 
        Most VPs I talk to say their biggest hurdle during growth is <b>{data['target']['weakness']}</b>. We've solved this—do you have a moment?"
        </div>""", unsafe_allow_html=True)

        st.write("** Voicemail Hook**")
        st.markdown(f"""<div class="script-block">
        "Hi [Name], I have a specific insight regarding {data['target']['name']}'s <b>{data['target']['weakness']}</b> and its impact on your 2026 goals. <br><br>
        I'll follow up with an email under the subject line: <b>{data['target']['name']} Strategy</b>."
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    else: st.error("Audit failed. Ensure URLs are valid.")
