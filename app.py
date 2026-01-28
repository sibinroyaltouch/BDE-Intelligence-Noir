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

# --- 2. ROBUST NAME EXTRACTION UTILITY ---
def get_clean_name(url):
    """Extracts the actual brand name from a URL, handling various formats."""
    # Remove protocol
    clean = re.sub(r'^https?://', '', url.lower())
    # Remove www.
    clean = re.sub(r'^www\.', '', clean)
    # Get the part before the first dot
    parts = clean.split('.')
    if parts:
        name = parts[0]
        # Common edge case: if the URL was 'co.uk', parts[0] is 'google' for 'google.co.uk'
        return name.capitalize()
    return "Entity"

# --- 3. DATABASE LOGIC (Noir Vault) ---
def init_db():
    conn = sqlite3.connect('intelligence.db')
    c = conn.cursor()
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

# --- 4. NOIR DESIGN SYSTEM (Strict Black/White High Contrast) ---
st.set_page_config(page_title="ABI Command Noir v20.0", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    
    .stApp { background-color: #000000 !important; font-family: 'Inter', sans-serif; }

    /* Outer Titles */
    .main-title { text-align: center; letter-spacing: 12px; font-weight: 900; color: #FFFFFF !important; margin-bottom: 5px; }
    .main-subtitle { text-align: center; color: #888888 !important; font-size: 0.9rem; margin-bottom: 40px; }

    /* Main Submit Button: White background, Black text */
    .stButton>button {
        background-color: #FFFFFF !important; color: #000000 !important;
        font-weight: 900 !important; border-radius: 2px !important;
        width: 100%; border: none !important; padding: 20px !important;
        text-transform: uppercase; letter-spacing: 3px; transition: 0.3s ease;
    }
    .stButton>button:hover { background-color: #CCCCCC !important; }

    /* Input boxes */
    .stTextInput>div>div>input { background-color: #000000 !important; color: #FFFFFF !important; border: 1px solid #FFFFFF !important; }

    /* White Module Containers (FORCE BLACK TEXT) */
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

    /* Code/Script Blocks */
    .script-block { background-color: #F5F5F5; border: 1px solid #000000; padding: 25px; font-family: 'Courier New', monospace; color: #000000 !important; font-weight: 600; margin-bottom: 15px; }
    
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

        # Resolve Entity Names correctly
        target_name = get_clean_name(self.target_url)
        my_name = get_clean_name(self.my_url)

        # Scrape My Services
        offer_map = {"Cloud": ["aws", "cloud", "devops"], "AI": ["ai", "automation"], "Cyber": ["security"], "CRM": ["salesforce", "hubspot"]}
        my_strengths = [k for k, v in offer_map.items() if any(x in m_data['text'] for x in v)]
        
        # Scrape Target Careers for Gaps
        career_text = ""
        for a in t_data['soup'].find_all('a', href=True):
            if any(x in a['href'].lower() for x in ['career', 'job']):
                c_res = self.fetch(urljoin(self.target_url, a['href']))
                if c_res: career_text = c_res['text']
                break

        tech_list = ["Salesforce", "AWS", "HubSpot", "Zendesk", "Shopify", "WordPress", "SAP", "Oracle"]
        found_tech = [x for x in tech_list if x.lower() in t_data['html']]
        
        weakness = "Fragmented Manual Workflows"
        if "wordpress" in t_data['html']: weakness = "Legacy Framework Technical Debt"
        elif "engineer" in career_text and not found_tech: weakness = "Infrastructure Readiness Gap"

        return {
            "target": {
                "name": target_name,
                "industry": "High-Tech / Enterprise" if "platform" in t_data['text'] else "Commercial Services",
                "tech": found_tech,
                "hiring": "Growth-Intensive" if len(career_text) > 1000 else "Stable Operations",
                "weakness": weakness,
                "url": self.target_url
            },
            "me": {"name": my_name, "services": my_strengths if my_strengths else ["Consultancy"], "url": self.my_url}
        }

# --- 6. SIDEBAR ADMIN ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>🛡️ ADMIN VAULT</h2>", unsafe_allow_html=True)
    admin_password = st.text_input("Vault Password", type="password")
    if admin_password == "Sibin@8129110807":
        st.success("Authorized")
        st.dataframe(get_vault_history())
    elif admin_password != "": st.error("Denied")

# --- 7. FRONTEND PAGE LAYOUT ---
st.markdown("<h1 class='main-title'>ABI COMMAND NOIR</h1>", unsafe_allow_html=True)
st.markdown("<p class='main-subtitle'>Enterprise Strategic Intelligence • War Room Dossier v20.0</p>", unsafe_allow_html=True)

col_a, col_b = st.columns(2)
with col_a: t_input = st.text_input("TARGET COMPANY URL", placeholder="e.g. google.com")
with col_b: m_input = st.text_input("YOUR COMPANY URL", placeholder="e.g. salesforce.com")

if st.button("Execute Strategic Audit"):
    engine = TitanIntelligence(t_input, m_input)
    with st.spinner("INITIATING SECURE CRAWL..."):
        data = engine.analyze()
        if data:
            save_to_vault(data['target']['url'], data['me']['url'])
    
    if data:
        # --- KPI BAR ---
        st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-item"><h4>Lead Status</h4><h2>High</h2></div>
                <div class="kpi-item"><h4>Target Account</h4><h2>{data['target']['name']}</h2></div>
                <div class="kpi-item"><h4>Industry</h4><h2>{data['target']['industry']}</h2></div>
                <div class="kpi-item"><h4>Vault</h4><h2>Logged</h2></div>
            </div>
        """, unsafe_allow_html=True)

        # --- 1. TARGET INTELLIGENCE PROFILE ---
        st.markdown('<div class="white-module">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">Target Intelligence Profile</div>', unsafe_allow_html=True)
        p1, p2 = st.columns(2)
        with p1:
            st.write(f"**Account Name:** {data['target']['name']}")
            st.write(f"**Primary Sector:** {data['target']['industry']}")
            st.write(f"**Hiring Posture:** {data['target']['hiring']}")
        with p2:
            st.write(f"**Internal Tech Stack:** {', '.join(data['target']['tech']) if data['target']['tech'] else 'Custom Infrastructure'}")
            st.write(f"**Loophole Detected:** {data['target']['weakness']}")
        st.markdown('</div>', unsafe_allow_html=True)

        # --- 2. SWOT & MARKET ANALYSIS ---
        st.markdown('<div class="white-module">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">SWOT & Loophole Analysis</div>', unsafe_allow_html=True)
        s1, s2 = st.columns(2)
        with s1:
            st.write(f"🟢 **[S] Strength:** Resilience in {data['target']['industry']} sector.")
            st.write(f"🔴 **[W] Weakness:** {data['target']['weakness']}.")
        with s2:
            st.write(f"🔵 **[O] Opportunity:** Strategic integration with {data['me']['services'][0]}.")
            st.write(f"🟡 **[T] Threat:** Sector agile competitors scaling via modern digital frameworks.")
        st.markdown('</div>', unsafe_allow_html=True)

        # --- 3. THE STRATEGIC BRIDGE ---
        st.markdown(f"""
            <div class="white-module">
                <div class="module-title">Strategic Bridge: {data['me']['name']} → {data['target']['name']}</div>
                <p><b>Observation:</b> {data['target']['name']} is scaling during <b>{data['target']['hiring']}</b> but is currently hindered by <b>{data['target']['weakness']}</b>.</p>
                <p><b>The Match:</b> As <b>{data['me']['name']}</b> is an expert in <b>{data['me']['services'][0]}</b>, your strength is the direct solution to their weakness.</p>
            </div>
        """, unsafe_allow_html=True)

        # --- 4. LINKEDIN STAKEHOLDER RADAR ---
        st.markdown('<div class="white-module">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">LinkedIn Stakeholder Radar</div>', unsafe_allow_html=True)
        st.write(f"High-Value Stakeholders at **{data['target']['name']}**:")
        roles = ["CTO", "VP Operations", "Head of Digital Transformation", "COO"]
        r_cols = st.columns(4)
        for i, r in enumerate(roles):
            with r_cols[i]:
                st.write(f"**{r}**")
                q = urllib.parse.quote(f"{data['target']['name']} {r}")
                st.markdown(f'<a href="https://www.linkedin.com/search/results/people/?keywords={q}" target="_blank" style="color:blue!important; text-decoration:underline; font-weight:bold;">🔍 Search Person</a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # --- 5. SALES PLAYBOOK (SCRIPTS) ---
        st.markdown('<div class="white-module">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">Sales Execution Playbook</div>', unsafe_allow_html=True)
        st.write("**📧 Professional Email Hook**")
        st.markdown(f"""<div class="script-block">
        Subject: Question regarding {data['target']['name']}'s {data['target']['hiring'].split()[0]} roadmap<br><br>
        "Hi [Name], I noticed your recent leadership regarding {data['target']['name']}'s footprint in {data['target']['industry']}.<br><br>
        Usually, firms scaling this fast while leveraging <b>{data['target']['tech'][0] if data['target']['tech'] else 'legacy tools'}</b> hit a bottleneck with <b>{data['target']['weakness']}</b>. <br><br>
        At <b>{data['me']['name']}</b>, we've helped similar firms bridge this gap. Do you have 2 minutes Tuesday?"
        </div>""", unsafe_allow_html=True)
        
        st.write("**☎️ Tele-Calling Script**")
        st.markdown(f"""<div class="script-block">
        "Hi [Name], it's [YourName] from {data['me']['name']}. I'm calling because I noticed you're scaling your team. 
        Most VPs I talk to say their biggest hurdle during growth is <b>{data['target']['weakness']}</b>. We've solved this—do you have a moment?"
        </div>""", unsafe_allow_html=True)

        st.write("**📟 Voicemail Hook**")
        st.code(f"Hi [Name], I have a specific insight regarding {data['target']['name']}'s {data['target']['weakness']} and its impact on your 2026 goals. I'll follow up with an email under the subject: {data['target']['name']} Strategy.")
        st.markdown('</div>', unsafe_allow_html=True)

    else: st.error("Audit failed. Ensure URLs are reachable.")
