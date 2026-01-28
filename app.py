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

# --- 2. DATABASE LOGIC (FIXED FOR REDACTED ERRORS) ---
def init_db():
    conn = sqlite3.connect('intelligence.db')
    c = conn.cursor()
    # If the table exists but is old, we drop it to apply the new column format
    # This prevents the "OperationalError" you encountered
    try:
        c.execute("SELECT my_url FROM history LIMIT 1")
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
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    c.execute("INSERT INTO history (date, time, target_url, my_url) VALUES (?, ?, ?, ?)", 
              (date_str, time_str, target_url, my_url))
    conn.commit()
    conn.close()

def get_vault_history():
    conn = sqlite3.connect('intelligence.db')
    # Exact column structure requested
    df = pd.read_sql_query("SELECT date as 'Date', time as 'Time', target_url as 'Targeted Company URL', my_url as 'My Company URL' FROM history ORDER BY id DESC", conn)
    conn.close()
    return df

init_db()

# --- 3. THE NOIR DESIGN SYSTEM (Strict Black & White) ---
st.set_page_config(page_title="Strategic ABI Command Noir", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    .stApp { background-color: #000000 !important; font-family: 'Inter', sans-serif; }
    
    /* Main Headings */
    .main-title { text-align: center; letter-spacing: 12px; font-weight: 900; color: #FFFFFF !important; margin-bottom: 5px; }
    .main-subtitle { text-align: center; color: #888888 !important; font-size: 0.9rem; margin-bottom: 40px; }

    /* Button Styling: White background, Black text */
    .stButton>button {
        background-color: #FFFFFF !important; color: #000000 !important;
        font-weight: 900 !important; border-radius: 2px !important;
        width: 100%; border: none !important; padding: 20px !important;
        text-transform: uppercase; letter-spacing: 3px;
    }

    /* Input boxes */
    .stTextInput>div>div>input { background-color: #000000 !important; color: #FFFFFF !important; border: 1px solid #FFFFFF !important; }

    /* White Module Containers (FORCE BLACK TEXT) */
    .white-module { background-color: #FFFFFF !important; padding: 45px; margin-bottom: 40px; border-radius: 0px; }
    .white-module h1, .white-module h2, .white-module h3, .white-module h4, 
    .white-module p, .white-module li, .white-module span, 
    .white-module div, .white-module b, .white-module label { 
        color: #000000 !important; 
    }

    .module-title { font-size: 1.8rem; font-weight: 900; text-transform: uppercase; border-bottom: 3px solid #000000; padding-bottom: 10px; margin-bottom: 30px; }

    /* KPI Bar - High Contrast */
    .kpi-container { display: flex; justify-content: space-around; background-color: #FFFFFF !important; padding: 35px; margin-bottom: 40px; text-align: center; }
    .kpi-item h4 { color: #000000 !important; font-size: 0.75rem !important; font-weight: 700 !important; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 5px;}
    .kpi-item h2 { color: #000000 !important; font-size: 2.2rem !important; font-weight: 900 !important; margin: 0; }

    .script-block { background-color: #F5F5F5; border: 1px solid #000000; padding: 25px; font-family: 'Courier New', monospace; color: #000000 !important; font-weight: 500; }
    
    [data-testid="stSidebar"] { background-color: #111111 !important; color: white !important; border-right: 1px solid #333333; }
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
            return {"html": res.text.lower(), "text": soup.get_text().lower(), "soup": soup, "url": url}
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

        # 1. Scrape MY Solutions
        my_offer_keys = {"Cloud": ["aws", "cloud", "devops"], "AI": ["ai", "machine"], "Cyber": ["security"], "CRM": ["salesforce", "hubspot"]}
        my_strengths = [k for k, v in my_offer_keys.items() if any(x in m_data['text'] for x in v)]
        
        # 2. Scrape TARGET Data
        career_text = ""
        for a in t_data['soup'].find_all('a', href=True):
            if any(x in a['href'].lower() for x in ['career', 'job']):
                c_res = self.fetch(urljoin(self.target_url, a['href']))
                if c_res: career_text = c_res['text']
                break

        tech_list = ["Salesforce", "AWS", "HubSpot", "Zendesk", "Shopify", "WordPress", "SAP"]
        found_tech = [x for x in tech_list if x.lower() in t_data['html']]
        
        # 3. Decision Logic
        weakness = "Fragmented Growth Bottleneck"
        if "wordpress" in t_data['html']: weakness = "Technical Debt / Security Risks"
        
        return {
            "target": {
                "name": self.target_url.split('.')[1].capitalize() if '.' in self.target_url else "Entity",
                "industry": "Enterprise Tech / SaaS" if "platform" in t_data['text'] else "Commercial Services",
                "tech": found_tech,
                "hiring": "High Intensity" if len(career_text) > 1500 else "Stable",
                "weakness": weakness,
                "news": self.get_news(self.target_url.split('.')[1] if '.' in self.target_url else "Company"),
                "url": self.target_url
            },
            "me": {"name": self.my_url.split('.')[1].capitalize(), "services": my_strengths if my_strengths else ["Strategic Modernization"], "url": self.my_url}
        }

# --- 5. SIDEBAR (ADMIN VAULT) ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>🛡️ ADMIN VAULT</h2>", unsafe_allow_html=True)
    admin_password = st.text_input("Vault Password", type="password")
    if admin_password == "Sibin@8129110807":
        st.success("Authorized")
        st.write("**Search History Log**")
        history_df = get_vault_history()
        if not history_df.empty:
            st.dataframe(history_df, use_container_width=True)
        else:
            st.info("No records found.")
    elif admin_password != "":
        st.error("Access Denied")

# --- 6. FRONTEND ---
st.markdown("<h1 class='main-title'>ABI COMMAND NOIR</h1>", unsafe_allow_html=True)
st.markdown("<p class='main-subtitle'>Strategic War Room • Enterprise Intelligence Dossier</p>", unsafe_allow_html=True)

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
        # --- TOP KPI BAR ---
        st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-item"><h4>Lead Status</h4><h2>High</h2></div>
                <div class="kpi-item"><h4>Target Name</h4><h2>{data['target']['name']}</h2></div>
                <div class="kpi-item"><h4>Industry</h4><h2>{data['target']['industry']}</h2></div>
                <div class="kpi-item"><h4>Vault</h4><h2>Logged</h2></div>
            </div>
        """, unsafe_allow_html=True)

        # --- SINGLE PAGE DOSSIER MODULES ---
        st.markdown(f"""
            <div class="white-module">
                <div class="module-title">Strategic Bridge: {data['me']['name']} → {data['target']['name']}</div>
                <p><b>Business Audit:</b> {data['target']['name']} is hiring for <b>{data['target']['hiring']}</b> but relies on <b>{data['target']['weakness']}</b>.</p>
                <p><b>Alignment:</b> As <b>{data['me']['name']}</b> is an expert in <b>{data['me']['services'][0]}</b>, we solve their scaling friction.</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="white-module">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">Account Intelligence Dossier</div>', unsafe_allow_html=True)
        st.write(f"**Industry Vertical:** {data['target']['industry']}")
        st.write(f"**Identified Tech Stack:** {', '.join(data['target']['tech']) if data['target']['tech'] else 'Custom Infrastructure'}")
        st.write(f"**Hiring Posture:** {data['target']['hiring']}")
        st.divider()
        st.write("**SWOT Insight:**")
        st.write(f"🟢 **Strength:** Scale in {data['target']['industry']}")
        st.write(f"🔴 **Weakness:** {data['target']['weakness']}")
        st.write(f"🔵 **Opportunity:** Integration with {data['me']['services'][0]}")
        st.divider()
        st.write("**Intelligence Headlines:**")
        for n in data['target']['news']: st.write(f"• {n}")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="white-module">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">Sales Playbook (Scripts)</div>', unsafe_allow_html=True)
        st.write("**📧 Professional Email Pitch**")
        st.code(f"Subject: Question regarding {data['target']['name']}'s {data['target']['hiring'].split()[0]} growth")
        st.markdown(f"""<div class="script-block">
        "Hi [Name], I saw your recent focus on {data['target']['hiring']}. <br>
        Usually, scaling firms hit a bottleneck with <b>{data['target']['weakness']}</b>. <br>
        At <b>{data['me']['name']}</b>, we help bridge this gap with {data['me']['services'][0]}. Do you have 2 minutes Tuesday?"
        </div>""", unsafe_allow_html=True)
        
        st.write("**☎️ Tele-Calling & Voicemail**")
        st.markdown(f"""<div class="script-block">
        "Hi [Name], it's [YourName] from {data['me']['name']}. I noticed you're scaling your team. 
        Most VPs I talk to say their biggest hurdle is <b>{data['target']['weakness']}</b>. We've solved this—do you have a moment?"
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="white-module">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">LinkedIn Stakeholder Search</div>', unsafe_allow_html=True)
        roles = ["CTO", "VP Operations", "Head of Digital"]
        r_cols = st.columns(3)
        for i, r in enumerate(roles):
            q = urllib.parse.quote(f"{data['target']['name']} {r}")
            r_cols[i].markdown(f'<a href="https://www.linkedin.com/search/results/people/?keywords={q}" target="_blank" style="color:blue!important; font-weight:bold; text-decoration:underline;">🔍 Search {r}</a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    else: st.error("Audit failed. Ensure URLs are reachable.")
