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
    clean = re.sub(r'^https?://', '', url.lower())
    clean = re.sub(r'^www\.', '', clean)
    parts = clean.split('.')
    return parts[0].capitalize() if parts else "Entity"

# --- 3. DATABASE LOGIC ---
def init_db():
    conn = sqlite3.connect('intelligence.db')
    c = conn.cursor()
    try:
        c.execute("SELECT target_url FROM history LIMIT 1")
    except sqlite3.OperationalError:
        c.execute("DROP TABLE IF EXISTS history")
    c.execute('''CREATE TABLE IF NOT EXISTS history 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, time TEXT, target_url TEXT, my_url TEXT)''')
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
    df = pd.read_sql_query("SELECT date as 'Date', time as 'Time', target_url as 'Targeted URL', my_url as 'My URL' FROM history ORDER BY id DESC", conn)
    conn.close()
    return df

init_db()

# --- 4. NOIR DESIGN SYSTEM (High Contrast & Mobile Responsive) ---
st.set_page_config(page_title="ABI Command Noir Pro", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    
    /* Pure Black App Background */
    .stApp { background-color: #000000 !important; font-family: 'Inter', sans-serif; }

    /* White text for main UI labels */
    h1, h2, h3, h4, p, label, span, div, .stMarkdown { color: #FFFFFF; }

    /* Responsive KPI Cards */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-bottom: 40px;
    }
    .kpi-card {
        background-color: #FFFFFF !important;
        padding: 25px;
        text-align: center;
        border-radius: 4px;
    }
    .kpi-card h4 { 
        color: #000000 !important; font-size: 0.75rem !important; 
        font-weight: 700 !important; letter-spacing: 2px; 
        text-transform: uppercase; margin: 0 0 10px 0 !important;
    }
    .kpi-card h2 { 
        color: #000000 !important; font-size: 1.8rem !important; 
        font-weight: 900 !important; margin: 0 !important;
    }

    /* White Module Containers (FORCE ALL TEXT BLACK) */
    .white-module { 
        background-color: #FFFFFF !important; 
        padding: 40px; 
        margin-bottom: 40px; 
        border-radius: 2px; 
    }
    .white-module h1, .white-module h2, .white-module h3, .white-module h4, 
    .white-module p, .white-module li, .white-module span, 
    .white-module div, .white-module b, .white-module label { 
        color: #000000 !important; 
    }

    .module-title { 
        font-size: 1.6rem; font-weight: 900; 
        text-transform: uppercase; border-bottom: 3px solid #000000; 
        padding-bottom: 10px; margin-bottom: 25px; color: #000000 !important; 
    }

    /* Primary Action Button */
    .stButton>button {
        background-color: #FFFFFF !important; color: #000000 !important;
        font-weight: 900 !important; border-radius: 4px !important;
        width: 100%; border: none !important; padding: 18px !important;
        text-transform: uppercase; letter-spacing: 2px;
    }

    /* Input Field Styling */
    .stTextInput>div>div>input { background-color: #000000 !important; color: #FFFFFF !important; border: 1px solid #FFFFFF !important; }

    /* Script Boxes inside White Modules */
    .script-block { 
        background-color: #F0F0F0; border: 1px solid #000000; 
        padding: 25px; font-family: 'Courier New', monospace; 
        color: #000000 !important; font-weight: 600; 
        margin-top: 10px; margin-bottom: 20px;
    }
    
    [data-testid="stSidebar"] { background-color: #111111 !important; color: white !important; border-right: 1px solid #333333; }
    .block-container { max-width: 1200px; padding-top: 2rem; margin: auto; }
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

    def get_news(self, query):
        url = f"https://news.google.com/rss/search?q={query}+when:7d&hl=en-US&gl=US&ceid=US:en"
        try:
            res = requests.get(url, timeout=5)
            soup = BeautifulSoup(res.text, 'xml')
            return [i.title.text for i in soup.find_all('item')[:3]]
        except: return ["No recent market news identified."]

    def analyze(self):
        t_data = self.fetch(self.target_url)
        m_data = self.fetch(self.my_url)
        if not t_data or not m_data: return None

        target_name = get_clean_name(self.target_url)
        my_name = get_clean_name(self.my_url)

        # Scrape Self Services
        offer_map = {"Cloud Integration": ["aws", "cloud", "devops"], "AI Automation": ["ai", "automation"], "Cybersecurity": ["security", "soc"], "CRM Optimization": ["salesforce", "hubspot"]}
        my_strengths = [k for k, v in offer_map.items() if any(x in m_data['text'] for x in v)]
        
        # Scrape Target Tech
        tech_list = ["Salesforce", "AWS", "HubSpot", "Zendesk", "Shopify", "WordPress", "Oracle", "SAP"]
        found_tech = [x for x in tech_list if x.lower() in t_data['html']]
        
        weakness = "Operational Fragmentation"
        if "wordpress" in t_data['html']: weakness = "Legacy Framework Technical Debt"

        return {
            "target": {
                "name": target_name,
                "industry": "High-Tech / SaaS" if "platform" in t_data['text'] else "Enterprise Services",
                "tech": found_tech,
                "hiring": "Growth-Intensive" if "career" in t_data['html'] else "Stable Operations",
                "weakness": weakness,
                "news": self.get_news(target_name),
                "url": self.target_url
            },
            "me": {"name": my_name, "services": my_strengths if my_strengths else ["Digital Strategic Modernization"], "url": self.my_url}
        }

# --- 6. SIDEBAR ADMIN ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>🛡️ ADMIN VAULT</h2>", unsafe_allow_html=True)
    admin_password = st.text_input("Vault Password", type="password")
    if admin_password == "Sibin@8129110807":
        st.success("Access Granted")
        st.dataframe(get_vault_history())
    elif admin_password != "": st.error("Unauthorized")

# --- 7. FRONTEND DASHBOARD ---
st.markdown("<h1 class='main-title'>ABI COMMAND NOIR</h1>", unsafe_allow_html=True)
st.markdown("<p class='main-subtitle'>Enterprise Strategic War Room Dossier • v22.0 Final</p>", unsafe_allow_html=True)

col_a, col_b = st.columns(2)
with col_a: t_input = st.text_input("TARGET URL", placeholder="e.g. google.com")
with col_b: m_input = st.text_input("YOUR URL", placeholder="e.g. salesforce.com")

if st.button("RUN STRATEGIC AUDIT"):
    engine = TitanIntelligence(t_input, m_input)
    with st.spinner("INITIATING SECURE SCAN..."):
        data = engine.analyze()
        if data: save_to_vault(data['target']['name'], data['me']['name'])
    
    if data:
        # --- RESPONSIVE KPI GRID ---
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
                <p><b>Executive Observation:</b> {data['target']['name']} is hiring for <b>{data['target']['hiring']}</b> but is currently hindered by <b>{data['target']['weakness']}</b>.</p>
                <p><b>Alignment:</b> As <b>{data['me']['name']}</b> is an expert in <b>{data['me']['services'][0]}</b>, your strength is the direct solution to their operational loophole.</p>
            </div>
        """, unsafe_allow_html=True)

        # --- MODULE 2: TARGET INTELLIGENCE ---
        st.markdown('<div class="white-module">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">Target Intelligence Profile</div>', unsafe_allow_html=True)
        p1, p2 = st.columns(2)
        with p1:
            st.write(f"**Entity Name:** {data['target']['name']}")
            st.write(f"**Industry Vertical:** {data['target']['industry']}")
            st.write(f"**Hiring Posture:** {data['target']['hiring']}")
        with p2:
            st.write("**Identified Internal Tech:**")
            st.write(", ".join(data['target']['tech']) if data['target']['tech'] else "Custom Stack")
            st.write(f"**Primary Weakness:** {data['target']['weakness']}")
        st.markdown('</div>', unsafe_allow_html=True)

        # --- MODULE 3: SWOT & NEWS ---
        st.markdown('<div class="white-module">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">SWOT & Market Sentiment</div>', unsafe_allow_html=True)
        s1, s2 = st.columns(2)
        with s1:
            st.write(f"🟢 **[S] Strength:** Adoption of {data['target']['tech'][0] if data['target']['tech'] else 'digital infrastructure'}.")
            st.write(f"🔴 **[W] Weakness:** {data['target']['weakness']}.")
        with s2:
            st.write(f"🔵 **[O] Opportunity:** Strategic scaling via {data['me']['services'][0]}.")
            st.write(f"🟡 **[T] Threat:** Agile competitors scaling faster via modern frameworks.")
        st.divider()
        st.write("**Market News Triggers:**")
        for n in data['target']['news']: st.write(f"• {n}")
        st.markdown('</div>', unsafe_allow_html=True)

        # --- MODULE 4: STAKEHOLDER RADAR ---
        st.markdown('<div class="white-module">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">LinkedIn Stakeholder Radar</div>', unsafe_allow_html=True)
        st.write(f"Primary Decision Makers at **{data['target']['name']}**:")
        roles = ["Chief Technology Officer", "VP Operations", "Head of Digital", "COO"]
        r_cols = st.columns(4)
        for i, r in enumerate(roles):
            q = urllib.parse.quote(f"{data['target']['name']} {r}")
            r_cols[i].markdown(f'<a href="https://www.linkedin.com/search/results/people/?keywords={q}" target="_blank" style="color:blue!important; text-decoration:underline; font-weight:bold;">🔍 Search {r}</a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # --- MODULE 5: SALES PLAYBOOK ---
        st.markdown('<div class="white-module">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">Sales Execution Playbook</div>', unsafe_allow_html=True)
        
        st.write("**📧 Professional Email Hook**")
        st.markdown(f"""<div class="script-block">
        Subject: Question regarding {data['target']['name']}'s focus on {data['target']['hiring'].split()[0]} growth<br><br>
        "Hi [Name], I noticed {data['target']['name']}'s recent focus on scaling. Usually, firms growing this fast while leveraging legacy tools hit a bottleneck with <b>{data['target']['weakness']}</b>. <br><br>
        At <b>{data['me']['name']}</b>, we've helped similar firms bridge this specific gap. Do you have 2 minutes Tuesday?"
        </div>""", unsafe_allow_html=True)
        
        st.write("**☎️ Tele-Calling Script**")
        st.markdown(f"""<div class="script-block">
        "Hi [Name], it's [YourName] from {data['me']['name']}. I'm calling because I noticed you're scaling your team. 
        Most VPs I talk to say their biggest hurdle during growth is <b>{data['target']['weakness']}</b>. We've solved this—do you have a moment?"
        </div>""", unsafe_allow_html=True)

        st.write("**📟 Voicemail Hook**")
        st.markdown(f"""<div class="script-block">
        "Hi [Name], I have a specific insight regarding {data['target']['name']}'s <b>{data['target']['weakness']}</b> and its impact on your 2026 goals. <br><br>
        I'll follow up with an email under the subject line: <b>{data['target']['name']} Strategy</b>."
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    else: st.error("Audit failed. Ensure URLs are valid.")
