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
    """Extracts the actual brand name from a URL, handling various formats."""
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
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, time TEXT, target_name TEXT, my_name TEXT)''')
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

# --- 4. NOIR ABSOLUTE DESIGN SYSTEM ---
st.set_page_config(page_title="ABI Strategic Noir", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    
    /* Pure Black App Background */
    .stApp { background-color: #000000 !important; font-family: 'Inter', sans-serif; }

    /* White text for global UI elements (Outside boxes) */
    h1, h2, h3, h4, p, label, span, div, .stMarkdown { color: #FFFFFF; }

    /* The "Absolute" White Module (Everything inside is BLACK) */
    .white-module {
        background-color: #FFFFFF !important;
        padding: 40px;
        border-radius: 4px;
        margin-bottom: 35px;
        color: #000000 !important;
    }
    
    /* Force every text tag inside white modules to Black */
    .white-module h1, .white-module h2, .white-module h3, .white-module h4, 
    .white-module p, .white-module li, .white-module span, 
    .white-module div, .white-module b, .white-module label, .white-module strong {
        color: #000000 !important;
    }

    .module-title {
        font-size: 1.8rem;
        font-weight: 900;
        text-transform: uppercase;
        border-bottom: 4px solid #000000;
        padding-bottom: 10px;
        margin-bottom: 25px;
        color: #000000 !important;
    }

    /* KPI Grid - Mobile Friendly & High Contrast */
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
    .kpi-card h4 { color: #000000 !important; font-size: 0.75rem !important; font-weight: 700 !important; letter-spacing: 2px; text-transform: uppercase; margin: 0 0 10px 0 !important; }
    .kpi-card h2 { color: #000000 !important; font-size: 1.8rem !important; font-weight: 900 !important; margin: 0 !important; }

    /* Submit Button: White background, Black text */
    .stButton>button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-weight: 900 !important;
        border-radius: 2px !important;
        width: 100%;
        border: none !important;
        padding: 20px !important;
        text-transform: uppercase;
        letter-spacing: 3px;
    }

    /* Script Blocks inside white modules */
    .script-block {
        background-color: #F5F5F5;
        border: 1px solid #000000;
        padding: 25px;
        font-family: 'Courier New', monospace;
        color: #000000 !important;
        font-weight: 600;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    /* Input Field */
    .stTextInput>div>div>input {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border: 1px solid #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] { background-color: #111111 !important; color: white !important; }
    .block-container { max-width: 1200px; padding-top: 3rem; margin: auto; }
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
        except: return ["No recent market triggers identified."]

    def analyze(self):
        t_data = self.fetch(self.target_url)
        m_data = self.fetch(self.my_url)
        if not t_data or not m_data: return None

        target_name = get_clean_name(self.target_url)
        my_name = get_clean_name(self.my_url)

        # Scrape My Strengths
        offer_map = {"Cloud Modernization": ["aws", "cloud", "devops"], "AI Engineering": ["ai", "machine"], "Cybersecurity": ["security", "soc"], "CRM Acceleration": ["salesforce", "hubspot"]}
        my_strengths = [k for k, v in offer_map.items() if any(x in m_data['text'] for x in v)]
        
        # Tech Audit
        tech_list = ["Salesforce", "AWS", "HubSpot", "Zendesk", "Shopify", "WordPress", "Oracle", "SAP"]
        found_tech = [x for x in tech_list if x.lower() in t_data['html']]
        
        weakness = "Growth Path Bottleneck"
        if "wordpress" in t_data['html']: weakness = "Legacy Technical Debt (Critical)"

        return {
            "target": {
                "name": target_name,
                "industry": "Enterprise Tech / SaaS" if "platform" in t_data['text'] else "Commercial Services",
                "tech": found_tech,
                "hiring": "Growth Mode" if "career" in t_data['html'] else "Steady State",
                "weakness": weakness,
                "news": self.get_news(target_name)
            },
            "me": {"name": my_name, "services": my_strengths if my_strengths else ["Strategic Digital Modernization"]}
        }

# --- 6. SIDEBAR ADMIN ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>🛡️ ADMIN VAULT</h2>", unsafe_allow_html=True)
    admin_password = st.text_input("Vault Key", type="password")
    if admin_password == "Sibin@8129110807":
        st.success("Authorized")
        st.dataframe(get_vault_history())
    elif admin_password != "": st.error("Invalid")

# --- 7. DASHBOARD FRONTEND ---
st.markdown("<h1 class='main-title'>ABI COMMAND NOIR</h1>", unsafe_allow_html=True)
st.markdown("<p class='main-subtitle'>Enterprise Strategic War Room Dossier • Strategic Insight v23.0</p>", unsafe_allow_html=True)

col_a, col_b = st.columns(2)
with col_a: target_input = st.text_input("TARGET URL", placeholder="e.g. google.com")
with col_b: my_input = st.text_input("YOUR URL", placeholder="e.g. yourcompany.com")

if st.button("Initiate Strategic Audit"):
    engine = TitanIntelligence(target_input, my_input)
    with st.spinner("EXECUTING SECURE CRAWL..."):
        data = engine.analyze()
        if data: save_to_vault(data['target']['name'], data['me']['name'])
    
    if data:
        # --- KPI GRID (WHITE BOX / BLACK TEXT) ---
        st.markdown(f"""
            <div class="kpi-grid">
                <div class="kpi-card"><h4>Lead Status</h4><h2>High Priority</h2></div>
                <div class="kpi-card"><h4>Target Account</h4><h2>{data['target']['name']}</h2></div>
                <div class="kpi-card"><h4>Industry</h4><h2>{data['target']['industry']}</h2></div>
                <div class="kpi-card"><h4>Vault</h4><h2>Secured</h2></div>
            </div>
        """, unsafe_allow_html=True)

        # --- MODULE 1: STRATEGIC BRIDGE ---
        st.markdown(f"""
            <div class="white-module">
                <div class="module-title">Strategic Bridge: {data['me']['name']} → {data['target']['name']}</div>
                <p><b>Executive Brief:</b> {data['target']['name']} is scaling during <b>{data['target']['hiring']}</b> but is currently hindered by <b>{data['target']['weakness']}</b>.</p>
                <p><b>Value Prop:</b> As <b>{data['me']['name']}</b> is an expert in <b>{data['me']['services'][0]}</b>, your strength is the direct solution to their weakness.</p>
            </div>
        """, unsafe_allow_html=True)

        # --- MODULE 2: TARGET PROFILE ---
        st.markdown('<div class="white-module">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">Account Intelligence Dossier</div>', unsafe_allow_html=True)
        p1, p2 = st.columns(2)
        with p1:
            st.write(f"**Entity Name:** {data['target']['name']}")
            st.write(f"**Market Sector:** {data['target']['industry']}")
            st.write(f"**Hiring Profile:** {data['target']['hiring']}")
        with p2:
            st.write(f"**Internal Tech:** {', '.join(data['target']['tech']) if data['target']['tech'] else 'Custom Infrastructure'}")
            st.write(f"**Operational Gap:** {data['target']['weakness']}")
        st.markdown('</div>', unsafe_allow_html=True)

        # --- MODULE 3: SWOT & NEWS ---
        st.markdown('<div class="white-module">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">SWOT & Market Sentiment</div>', unsafe_allow_html=True)
        s1, s2 = st.columns(2)
        with s1:
            st.write(f"🟢 **[S] Strength:** Resilience in {data['target']['industry']} landscape.")
            st.write(f"🔴 **[W] Weakness:** {data['target']['weakness']}.")
        with s2:
            st.write(f"🔵 **[O] Opportunity:** Strategic integration with {data['me']['services'][0]}.")
            st.write(f"🟡 **[T] Threat:** Sector agile competitors scaling via modern digital frameworks.")
        st.divider()
        st.write("**Recent Strategic Triggers:**")
        for n in data['target']['news']: st.write(f"• {n}")
        st.markdown('</div>', unsafe_allow_html=True)

        # --- MODULE 4: LINKEDIN RADAR ---
        st.markdown('<div class="white-module">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">LinkedIn Stakeholder Radar</div>', unsafe_allow_html=True)
        st.write(f"Primary Decision Makers at **{data['target']['name']}**:")
        roles = ["Chief Technology Officer", "VP Operations", "Head of Transformation", "COO"]
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
        Subject: Question regarding {data['target']['name']}'s {data['target']['hiring'].split()[0]} roadmap<br><br>
        "Hi [Name], I noticed {data['target']['name']}'s recent scale. Usually, firms growing this fast while leveraging legacy tools hit a bottleneck with <b>{data['target']['weakness']}</b>. <br><br>
        At <b>{data['me']['name']}</b>, we've helped similar firms bridge this gap. Do you have 2 minutes Tuesday?"
        </div>""", unsafe_allow_html=True)
        
        st.write("**☎️ Tele-Calling Script**")
        st.markdown(f"""<div class="script-block">
        "Hi [Name], it's [YourName] from {data['me']['name']}. I noticed you're scaling your team. 
        Most VPs I talk to say their biggest hurdle during growth is <b>{data['target']['weakness']}</b>. We've solved this—do you have a moment?"
        </div>""", unsafe_allow_html=True)

        st.write("**📟 Voicemail Hook**")
        st.markdown(f"""<div class="script-block">
        "Hi [Name], I have a specific insight regarding {data['target']['name']}'s <b>{data['target']['weakness']}</b> and its impact on your 2026 goals. <br><br>
        I'll follow up with an email under the subject line: <b>{data['target']['name']} Strategy</b>."
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    else: st.error("Audit failed. Ensure URLs are valid.")
