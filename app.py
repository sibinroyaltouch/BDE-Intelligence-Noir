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

# --- 2. SECURE DATABASE LOGIC (THE BACKEND) ---
def init_db():
    conn = sqlite3.connect('intelligence.db')
    c = conn.cursor()
    # Created a new table 'vault_logs' to handle the new URL tracking structure
    c.execute('''CREATE TABLE IF NOT EXISTS vault_logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  target_url TEXT, 
                  my_url TEXT, 
                  timestamp TEXT)''')
    conn.commit()
    conn.close()

def save_to_vault(target_url, my_url):
    conn = sqlite3.connect('intelligence.db')
    c = conn.cursor()
    # Capturing exact date and time
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO vault_logs (target_url, my_url, timestamp) VALUES (?, ?, ?)", 
              (target_url, my_url, now))
    conn.commit()
    conn.close()

def get_vault_history():
    conn = sqlite3.connect('intelligence.db')
    # Fetching the raw data
    df = pd.read_sql_query("SELECT timestamp, target_url, my_url FROM vault_logs ORDER BY id DESC", conn)
    conn.close()
    
    if not df.empty:
        # Formatting the columns exactly as requested: Date | Time | Target URL | My URL
        df['Date'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d')
        df['Time'] = pd.to_datetime(df['timestamp']).dt.strftime('%H:%M:%S')
        df = df[['Date', 'Time', 'target_url', 'my_url']]
        df.columns = ['Date', 'Time', 'Targeted Company URL', 'My Company URL']
    return df

# Initialize DB on Startup
init_db()

# --- 3. THE NOIR DESIGN SYSTEM ---
st.set_page_config(page_title="ABI Command Noir v17.5", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    .stApp { background-color: #000000 !important; font-family: 'Inter', sans-serif; }
    .main-title { text-align: center; letter-spacing: 12px; font-weight: 900; color: #FFFFFF !important; margin-bottom: 5px; }
    .main-subtitle { text-align: center; color: #888888 !important; font-size: 0.9rem; margin-bottom: 40px; }

    /* Button Styling */
    .stButton>button {
        background-color: #FFFFFF !important; color: #000000 !important;
        font-weight: 900 !important; border-radius: 2px !important;
        width: 100%; border: none !important; padding: 20px !important; 
        text-transform: uppercase; letter-spacing: 3px;
    }

    /* Input boxes */
    .stTextInput>div>div>input { background-color: #000000 !important; color: #FFFFFF !important; border: 1px solid #FFFFFF !important; }

    /* White Module Containers (Black Text Only) */
    .white-module { background-color: #FFFFFF !important; padding: 45px; margin-bottom: 40px; }
    .white-module h1, .white-module h2, .white-module h3, .white-module h4, .white-module p, 
    .white-module li, .white-module span, .white-module div, .white-module b { color: #000000 !important; }
    .module-title { font-size: 1.8rem; font-weight: 900; text-transform: uppercase; border-bottom: 3px solid #000000; padding-bottom: 10px; margin-bottom: 30px; }

    /* KPI Bar */
    .kpi-container { display: flex; justify-content: space-around; background-color: #FFFFFF !important; padding: 35px; margin-bottom: 40px; text-align: center; }
    .kpi-item h4 { color: #000000 !important; font-size: 0.75rem !important; font-weight: 700 !important; letter-spacing: 2px; margin-bottom: 5px; text-transform: uppercase; }
    .kpi-item h2 { color: #000000 !important; font-size: 2.2rem !important; font-weight: 900 !important; margin: 0; }

    .script-block { background-color: #F5F5F5; border: 1px solid #000000; padding: 25px; font-family: 'Courier New', monospace; color: #000000 !important; }
    .block-container { max-width: 1200px; padding-top: 3rem; margin: auto; }
    #MainMenu, footer {visibility: hidden;}

    /* Sidebar Admin Styles */
    [data-testid="stSidebar"] { background-color: #111111 !important; color: white !important; }
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
            res = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            return {"html": res.text.lower(), "text": soup.get_text().lower(), "soup": soup}
        except: return None

    def analyze(self):
        t_data = self.fetch(self.target_url)
        m_data = self.fetch(self.my_url)
        if not t_data or not m_data: return None

        my_offer_keys = {"Cloud & DevOps": ["aws", "cloud", "azure"], "AI & Automation": ["ai", "machine", "intelligence"], "Cybersecurity": ["security", "threat"], "CRM Tech": ["salesforce", "hubspot"]}
        my_strengths = [k for k, v in my_offer_keys.items() if any(x in m_data['text'] for x in v)]
        
        tech_list = ["Salesforce", "AWS", "HubSpot", "Zendesk", "Shopify", "WordPress", "React"]
        found_tech = [x for x in tech_list if x.lower() in t_data['html']]
        
        return {
            "target": {
                "name": self.target_url.split('.')[1].capitalize() if '.' in self.target_url else "Entity",
                "industry": "High-Tech / SaaS" if "platform" in t_data['text'] else "Enterprise Services",
                "tech": found_tech,
                "url": self.target_url
            },
            "me": {
                "name": self.my_url.split('.')[1].capitalize() if '.' in self.my_url else "MyCompany", 
                "services": my_strengths if my_strengths else ["Consultancy"],
                "url": self.my_url
            }
        }

# --- 5. SIDEBAR (ADMIN VAULT) ---
with st.sidebar:
    st.title("🛡️ ADMIN VAULT")
    st.write("Private Database Access")
    admin_password = st.text_input("Enter Vault Password", type="password")
    
    # --- PASSWORD UPDATED HERE ---
    if admin_password == "Sibin@8129110807": 
        st.success("Access Granted")
        st.subheader("Account Search History")
        history_df = get_vault_history()
        if not history_df.empty:
            # Displays the exact columns requested: Date | Time | Target URL | My URL
            st.dataframe(history_df, use_container_width=True, hide_index=True)
        else:
            st.write("No history found.")
    elif admin_password != "":
        st.error("Incorrect Password")

# --- 6. FRONTEND LAYOUT ---
st.markdown("<h1 class='main-title'>ABI COMMAND NOIR</h1>", unsafe_allow_html=True)
st.markdown("<p class='main-subtitle'>Enterprise Strategic Intelligence • Strategic War Room Dossier</p>", unsafe_allow_html=True)

col_a, col_b = st.columns(2)
with col_a: t_url = st.text_input("TARGET COMPANY URL", placeholder="e.g. apple.com")
with col_b: m_url = st.text_input("YOUR COMPANY URL", placeholder="e.g. salesforce.com")

if st.button("Execute Strategic Audit"):
    engine = TitanIntelligence(t_url, m_url)
    with st.spinner("INITIATING DEEP SCAN..."):
        data = engine.analyze()
        if data:
            # --- SAVING URLS DIRECTLY TO DATABASE ---
            save_to_vault(t_url, m_url)
    
    if data:
        # --- TOP KPI BAR ---
        st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-item"><h4>Lead Status</h4><h2>High</h2></div>
                <div class="kpi-item"><h4>Target Name</h4><h2>{data['target']['name']}</h2></div>
                <div class="kpi-item"><h4>Industry</h4><h2>{data['target']['industry']}</h2></div>
                <div class="kpi-item"><h4>Vault Status</h4><h2>Secured</h2></div>
            </div>
        """, unsafe_allow_html=True)

        # --- 1. THE STRATEGIC BRIDGE ---
        st.markdown(f"""
            <div class="white-module">
                <div class="module-title">Strategic Bridge: {data['me']['name']} → {data['target']['name']}</div>
                <p><b>Business Audit:</b> {data['target']['name']} relies on <b>{", ".join(data['target']['tech']) if data['target']['tech'] else "Custom Tools"}</b>.</p>
                <p><b>Solution Alignment:</b> Your expertise in <b>{data['me']['services'][0]}</b> directly addresses their scaling friction.</p>
            </div>
        """, unsafe_allow_html=True)

        # --- 2. SALES PLAYBOOK ---
        st.markdown('<div class="white-module">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">Sales Execution Playbook</div>', unsafe_allow_html=True)
        st.write("**📧 Professional Email Pitch**")
        st.markdown(f"""<div class="script-block">
        "Hi [Name], I noticed {data['target']['name']}'s recent footprint in {data['target']['industry']}.<br><br>
        We've helped similar firms use <b>{data['me']['services'][0]}</b> to optimize their workflow. Would you be open to a 2-minute chat?"
        </div>""", unsafe_allow_html=True)
        
        st.write("**☎️ Tele-Calling Script**")
        st.markdown(f"""<div class="script-block">
        "Hi [Name], it's [YourName] from {data['me']['name']}. I noticed you're scaling your team. We've solved friction points for similar {data['target']['industry']} accounts. Do you have a moment?"
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # --- 3. STAKEHOLDER SEARCH ---
        st.markdown('<div class="white-module">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">LinkedIn Stakeholder Radar</div>', unsafe_allow_html=True)
        roles = ["CTO", "VP Operations", "Head of Digital"]
        r_cols = st.columns(3)
        for i, r in enumerate(roles):
            q = urllib.parse.quote(f"{data['target']['name']} {r}")
            r_cols[i].markdown(f'<a href="https://www.linkedin.com/search/results/people/?keywords={q}" target="_blank" style="color:blue!important; font-weight:bold;">🔍 Search {r}</a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.error("Audit failed. Ensure URLs are valid.")
