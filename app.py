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

# --- 2. DATABASE LOGIC (Noir Vault) ---
def init_db():
    conn = sqlite3.connect('intelligence.db')
    c = conn.cursor()
    # Reset table if structure is old to prevent errors
    try:
        c.execute("SELECT target_url FROM history LIMIT 1")
    except sqlite3.OperationalError:
        c.execute("DROP TABLE IF EXISTS history")
        
    c.execute('''CREATE TABLE IF NOT EXISTS history 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  date TEXT, 
                  time TEXT, 
                  target_url TEXT,
                  my_url TEXT)''')
    conn.commit()
    conn.close()

def save_to_vault(target_url, my_url):
    conn = sqlite3.connect('intelligence.db')
    c = conn.cursor()
    now = datetime.now()
    c.execute("INSERT INTO history (date, time, target_url, my_url) VALUES (?, ?, ?, ?)", 
              (now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), target_url, my_url))
    conn.commit()
    conn.close()

def get_vault_history():
    conn = sqlite3.connect('intelligence.db')
    df = pd.read_sql_query("SELECT date as 'Date', time as 'Time', target_url as 'Targeted Company URL', my_url as 'My Company URL' FROM history ORDER BY id DESC", conn)
    conn.close()
    return df

init_db()

# --- 3. NOIR DESIGN SYSTEM (Strict Black/White) ---
st.set_page_config(page_title="ABI Strategic Command Noir", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    
    /* Global App Background */
    .stApp { background-color: #000000 !important; font-family: 'Inter', sans-serif; }

    /* Outer Headings */
    .main-title { text-align: center; letter-spacing: 12px; font-weight: 900; color: #FFFFFF !important; margin-bottom: 5px; }
    .main-subtitle { text-align: center; color: #888888 !important; font-size: 0.9rem; margin-bottom: 40px; }

    /* Button: White BG, Black Text */
    .stButton>button {
        background-color: #FFFFFF !important; color: #000000 !important;
        font-weight: 900 !important; border-radius: 2px !important;
        width: 100%; border: none !important; padding: 20px !important;
        text-transform: uppercase; letter-spacing: 3px;
    }

    /* Input boxes */
    .stTextInput>div>div>input { background-color: #000000 !important; color: #FFFFFF !important; border: 1px solid #FFFFFF !important; }

    /* White Module Containers (Black Text Only) */
    .white-module { background-color: #FFFFFF !important; padding: 45px; margin-bottom: 40px; border-radius: 0px; }
    .white-module h1, .white-module h2, .white-module h3, .white-module h4, 
    .white-module p, .white-module li, .white-module span, 
    .white-module div, .white-module b, .white-module label { 
        color: #000000 !important; 
    }

    .module-title { font-size: 1.8rem; font-weight: 900; text-transform: uppercase; border-bottom: 3px solid #000000; padding-bottom: 10px; margin-bottom: 30px; color: #000000 !important; }

    /* KPI Bar - High Contrast */
    .kpi-container { display: flex; justify-content: space-around; background-color: #FFFFFF !important; padding: 35px; margin-bottom: 40px; text-align: center; }
    .kpi-item h4 { color: #000000 !important; font-size: 0.75rem !important; font-weight: 700 !important; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 5px;}
    .kpi-item h2 { color: #000000 !important; font-size: 2.2rem !important; font-weight: 900 !important; margin: 0; }

    .script-block { background-color: #F5F5F5; border: 1px solid #000000; padding: 25px; font-family: 'Courier New', monospace; color: #000000 !important; }
    
    [data-testid="stSidebar"] { background-color: #111111 !important; color: white !important; }
    .block-container { max-width: 1200px; padding-top: 3rem; margin: auto; }
    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 4. INTELLIGENCE ENGINE ---
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

        # 1. Scrape My Services
        offer_map = {"Cloud": ["aws", "cloud", "devops"], "AI": ["ai", "automation"], "Cyber": ["security"], "CRM": ["salesforce", "hubspot"]}
        my_strengths = [k for k, v in offer_map.items() if any(x in m_data['text'] for x in v)]
        
        # 2. Scrape Target Sub-pages
        career_text = ""
        for a in t_data['soup'].find_all('a', href=True):
            if any(x in a['href'].lower() for x in ['career', 'job']):
                c_res = self.fetch(urljoin(self.target_url, a['href']))
                if c_res: career_text = c_res['text']
                break

        tech_list = ["Salesforce", "AWS", "HubSpot", "Zendesk", "Shopify", "WordPress", "SAP", "Oracle"]
        found_tech = [x for x in tech_list if x.lower() in t_data['html']]
        
        weakness = "Fragmented Workflow Efficiency"
        if "wordpress" in t_data['html']: weakness = "Legacy Technical Debt (Security Risk)"

        return {
            "target": {
                "name": self.target_url.split('.')[1].capitalize() if '.' in self.target_url else "Entity",
                "industry": "High-Tech / SaaS" if "platform" in t_data['text'] else "Enterprise Services",
                "tech": found_tech,
                "hiring": "Growth Mode" if len(career_text) > 1000 else "Stable",
                "weakness": weakness,
                "location": "Global Operations",
                "risk": "GDPR / Strict" if ".uk" in self.target_url or ".de" in self.target_url else "Standard CCPA",
                "url": self.target_url
            },
            "me": {"name": self.my_url.split('.')[1].capitalize(), "services": my_strengths if my_strengths else ["Strategic Modernization"], "url": self.my_url}
        }

# --- 5. SIDEBAR ADMIN VAULT ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>🛡️ ADMIN VAULT</h2>", unsafe_allow_html=True)
    admin_password = st.text_input("Password", type="password")
    if admin_password == "Sibin@8129110807":
        st.success("Authorized")
        history_df = get_vault_history()
        st.dataframe(history_df)
    elif admin_password != "":
        st.error("Denied")

# --- 6. FRONTEND LAYOUT ---
st.markdown("<h1 class='main-title'>Mr. BDE V 2.0 </h1> <br><sub><center> (Developed by Sibinkalliyath)</center></sub>", unsafe_allow_html=True)
st.markdown("<p class='main-subtitle'>Enterprise Strategic Intelligence War Room Dossier</p>", unsafe_allow_html=True)

col_a, col_b = st.columns(2)
with col_a: t_input = st.text_input("TARGET URL", placeholder="e.g. apple.com")
with col_b: m_input = st.text_input("YOUR URL", value="https://")

if st.button("Execute Strategic Audit"):
    engine = TitanIntelligence(t_input, m_input)
    with st.spinner("INITIATING SECURE CRAWL..."):
        data = engine.analyze()
        if data:
            save_to_vault(data['target']['url'], data['me']['url'])
    
    if data:
        # --- TOP KPI BAR (WHITE BOX / BLACK TEXT) ---
        st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-item"><h4>Lead Status</h4><h2>High</h2></div>
                <div class="kpi-item"><h4>Target Name</h4><h2>{data['target']['name']}</h2></div>
                <div class="kpi-item"><h4>Industry</h4><h2>{data['target']['industry']}</h2></div>
                <div class="kpi-item"><h4>Risk Profile</h4><h2>{data['target']['risk'].split()[0]}</h2></div>
            </div>
        """, unsafe_allow_html=True)

        # --- 1. TARGET INTELLIGENCE PROFILE ---
        st.markdown('<div class="white-module">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">Target Intelligence Profile</div>', unsafe_allow_html=True)
        p1, p2 = st.columns(2)
        with p1:
            st.write(f"**Entity Name:** {data['target']['name']}")
            st.write(f"**Industry Vertical:** {data['target']['industry']}")
            st.write(f"**Operational Scope:** {data['target']['location']}")
            st.write(f"**Legal Framework:** {data['target']['risk']}")
        with p2:
            st.write(f"**Internal Tech Stack:** {', '.join(data['target']['tech']) if data['target']['tech'] else 'Custom Infrastructure'}")
            st.write(f"**Hiring Posture:** {data['target']['hiring']}")
            st.write(f"**Identified Weakness:** {data['target']['weakness']}")
        st.markdown('</div>', unsafe_allow_html=True)

        # --- 2. THE STRATEGIC BRIDGE ---
        st.markdown(f"""
            <div class="white-module">
                <div class="module-title">Strategic Bridge: {data['me']['name']} → {data['target']['name']}</div>
                <p><b>Business Audit:</b> {data['target']['name']} is hiring for <b>{data['target']['hiring']}</b> but their infrastructure suggests a bottleneck in <b>{data['target']['weakness']}</b>.</p>
                <p><b>Solution Alignment:</b> As <b>{data['me']['name']}</b> is an expert in <b>{data['me']['services'][0]}</b>, we provide the specific tools needed to bypass their current weakness.</p>
            </div>
        """, unsafe_allow_html=True)

        # --- 3. LINKEDIN STAKEHOLDER RADAR ---
        st.markdown('<div class="white-module">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">LinkedIn Stakeholder Radar</div>', unsafe_allow_html=True)
        st.write("Target these Primary Decision Makers at **" + data['target']['name'] + "**:")
        roles = ["Chief Technology Officer", "VP Operations", "Head of Digital Transformation", "COO"]
        r_cols = st.columns(4)
        for i, r in enumerate(roles):
            with r_cols[i]:
                st.write(f"**{r}**")
                q = urllib.parse.quote(f"{data['target']['name']} {r}")
                st.markdown(f'<a href="https://www.linkedin.com/search/results/people/?keywords={q}" target="_blank" style="color:blue!important; text-decoration:underline; font-weight:bold;">🔍 Search Person</a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # --- 4. SALES PLAYBOOK (SCRIPTS) ---
        st.markdown('<div class="white-module">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">Sales Execution Playbook</div>', unsafe_allow_html=True)
        st.write("**📧 Professional Email Pitch**")
        st.markdown(f"""<div class="script-block">
        "Hi [Name], I noticed your focus on {data['target']['hiring']} growth at {data['target']['name']}.<br><br>
        Usually, firms hitting this scale experience friction in <b>{data['target']['weakness']}</b>. <br><br>
        We've helped similar firms use <b>{data['me']['services'][0]}</b> to recover 20% efficiency. Do you have 2 minutes Tuesday?"
        </div>""", unsafe_allow_html=True)
        
        st.write("**☎️ Tele-Calling Script**")
        st.markdown(f"""<div class="script-block">
        "Hi [Name], it's [YourName] from {data['me']['name']}. I'm calling because I noticed you're scaling your team. 
        Most VPs I talk to say their biggest hurdle during growth is <b>{data['target']['weakness']}</b>. We've solved this—do you have a moment?"
        </div>""", unsafe_allow_html=True)

        st.write("**📟 Voicemail Hook:**")
        st.code(f"Hi [Name], I have a specific insight regarding {data['target']['name']}'s {data['target']['weakness']} and its impact on your 2026 goals. I'll follow up with an email under the subject: {data['target']['name']} Strategy.")
        st.markdown('</div>', unsafe_allow_html=True)

    else: st.error("Audit failed. Check URLs.")
