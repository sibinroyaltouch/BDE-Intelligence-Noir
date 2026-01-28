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

# --- 2. DATABASE LOGIC (THE BACKEND) ---
def init_db():
    conn = sqlite3.connect('intelligence.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  target_name TEXT, 
                  target_url TEXT,
                  my_company TEXT, 
                  my_company_url TEXT,
                  timestamp TEXT)''')
    conn.commit()
    conn.close()

def save_to_vault(target_name, target_url, my_company_name, my_company_url):
    conn = sqlite3.connect('intelligence.db')
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO history (target_name, target_url, my_company, my_company_url, timestamp) VALUES (?, ?, ?, ?, ?)", 
              (target_name, target_url, my_company_name, my_company_url, now))
    conn.commit()
    conn.close()

def get_vault_history():
    conn = sqlite3.connect('intelligence.db')
    df = pd.read_sql_query("SELECT timestamp, target_url, my_company_url FROM history ORDER BY id DESC", conn)
    conn.close()
    
    if not df.empty:
        df[['Date', 'Time']] = df['timestamp'].str.split(' ', expand=True)
        df = df[['Date', 'Time', 'target_url', 'my_company_url']]
        df.columns = ['Date', 'Time', 'Targeted Company URL', 'Your Company URL'] # Rename columns for display
    
    return df

# Initialize DB on Startup
init_db()

# --- 3. THE NOIR DESIGN SYSTEM ---
st.set_page_config(page_title="Strategic ABI Noir v17.1", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    .stApp { background-color: #000000 !important; font-family: 'Inter', sans-serif; }
    .main-title { text-align: center; letter-spacing: 12px; font-weight: 900; color: #FFFFFF !important; margin-bottom: 5px; }
    .main-subtitle { text-align: center; color: #888888 !important; font-size: 0.9rem; margin-bottom: 40px; }

    /* Button Styling: White background, Black text */
    .stButton>button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-weight: 900 !important;
        border-radius: 2px !important;
        width: 100%; border: none !important;
        padding: 20px !important; text-transform: uppercase; letter-spacing: 3px;
    }

    /* Input boxes */
    .stTextInput>div>div>input { background-color: #000000 !important; color: #FFFFFF !important; border: 1px solid #FFFFFF !important; }

    /* White Module Containers (Black Text Only) */
    .white-module { background-color: #FFFFFF !important; padding: 45px; margin-bottom: 40px; }
    .white-module h1, .white-module h2, .white-module h3, .white-module h4, .white-module p, 
    .white-module li, .white-module span, .white-module div, .white-module b { color: #000000 !important; }

    .module-title { font-size: 1.8rem; font-weight: 900; text-transform: uppercase; border-bottom: 3px solid #000000; padding-bottom: 10px; margin-bottom: 30px; }

    /* KPI Bar - High Contrast White with Black Text */
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
            return {"html": res.text.lower(), "text": soup.get_text().lower(), "soup": soup, "url": url}
        except: return None

    def get_news(self, query):
        url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        try:
            res = requests.get(url, timeout=5)
            soup = BeautifulSoup(res.text, 'xml')
            return [i.title.text for i in soup.find_all('item')[:3]]
        except: return ["No recent major news identified."]

    def analyze(self):
        t_data = self.fetch(self.target_url)
        m_data = self.fetch(self.my_url)
        if not t_data or not m_data: return None

        # 1. Scrape MY Solutions/Offerings
        my_offer_keys = {
            "Cloud Transformation": ["aws", "cloud", "azure", "devops", "kubernetes"],
            "AI/Automation Intelligence": ["ai", "machine learning", "automation", "intelligence"],
            "Cybersecurity & Compliance": ["security", "encryption", "threat", "soc", "compliance"],
            "Sales/CRM Acceleration": ["salesforce", "hubspot", "crm", "lead gen", "pipeline"]
        }
        my_strengths = [k for k, v in my_offer_keys.items() if any(x in m_data['text'] for x in v)]
        if not my_strengths: my_strengths = ["Digital Business Modernization"]

        # 2. Scrape TARGET Data
        career_text = ""
        for a in t_data['soup'].find_all('a', href=True):
            if any(x in a['href'].lower() for x in ['career', 'job', 'join']):
                c_res = self.fetch(urljoin(self.target_url, a['href']))
                if c_res: career_text = c_res['text']
                break

        tech_list = ["Salesforce", "AWS", "HubSpot", "Zendesk", "Shopify", "WordPress", "Oracle", "SAP", "ServiceNow"]
        found_tech = [x for x in tech_list if x.lower() in t_data['html']]
        
        target_offers = []
        if "platform" in t_data['text'] or "saas" in t_data['text']: target_offers.append("Enterprise Platforms")
        if "bank" in t_data['text'] or "payment" in t_data['text']: target_offers.append("Financial Services")

        # 3. Weakness Heuristics
        weakness = "Operational Data Silos"
        if "wordpress" in t_data['html']: weakness = "Legacy Technical Debt (Security & Scaling Risk)"
        elif "engineer" in career_text and not found_tech: weakness = "Infrastructure Deficit for Scale"

        return {
            "target": {
                "name": self.target_url.split('.')[1].capitalize() if '.' in self.target_url else "Entity",
                "industry": "High-Tech / Enterprise" if "software" in t_data['text'] else "Commercial Services",
                "tech": found_tech,
                "offers": target_offers,
                "hiring": "Intensive Growth" if len(career_text) > 1500 else "Stable Operations",
                "weakness": weakness,
                "news": self.get_news(self.target_url.split('.')[1]),
                "location": "Global", # Placeholder for actual location detection
                "risk": "GDPR / Strict" if ".uk" in self.target_url or ".de" in self.target_url else "CCPA / Moderate",
                "url": self.target_url
            },
            "me": {"name": self.my_url.split('.')[1].capitalize(), "services": my_strengths, "url": self.my_url}
        }

# --- 5. SIDEBAR (ADMIN VAULT) ---
with st.sidebar:
    st.title("🛡️ ADMIN VAULT")
    st.write("Private Database Access")
    admin_password = st.text_input("Enter Vault Password", type="password")
    if admin_password == "Sibin@8129110807": # <--- ADMIN PASSWORD CHANGED HERE
        st.success("Access Granted")
        st.subheader("Account Search History")
        history_df = get_vault_history()
        if not history_df.empty:
            st.dataframe(history_df, use_container_width=True) # Use container width for better display
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

if st.button("EXECUTE STRATEGIC AUDIT"):
    engine = TitanIntelligence(t_url, m_url)
    with st.spinner("INITIATING DEEP SCAN..."):
        data = engine.analyze()
        if data:
            # SAVE TO BACKEND, including both URLs
            save_to_vault(data['target']['name'], data['target']['url'], data['me']['name'], data['me']['url'])
    
    if data:
        # --- TOP KPI BAR ---
        st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-item"><h4>Lead Status</h4><h2>High</h2></div>
                <div class="kpi-item"><h4>Target Name</h4><h2>{data['target']['name']}</h2></div>
                <div class="kpi-item"><h4>Industry</h4><h2>{data['target']['industry']}</h2></div>
                <div class="kpi-item"><h4>Risk Profile</h4><h2>{data['target']['risk'].split('/')[0]}</h2></div>
            </div>
        """, unsafe_allow_html=True)

        # --- 1. THE STRATEGIC BRIDGE ---
        st.markdown(f"""
            <div class="white-module">
                <div class="module-title">Strategic Bridge: {data['me']['name']} → {data['target']['name']}</div>
                <p><b>Business Audit:</b> {data['target']['name']} is currently focused on <b>{data['target']['hiring']}</b> within the <b>{data['target']['industry']}</b> sector, but their infrastructure suggests a bottleneck in <b>{data['target']['weakness']}</b>.</p>
                <p><b>Solution Alignment:</b> As <b>{data['me']['name']}</b> is an expert in <b>{data['me']['services'][0]}</b>, your strength directly addresses their operational loophole, offering a clear path to enhanced efficiency and scalability.</p>
                <p><b>The Wedge:</b> Pitch a cost-benefit analysis for {data['me']['services'][0]} to mitigate their {data['target']['weakness']} and accelerate their {data['target']['hiring']} initiatives.</p>
            </div>
        """, unsafe_allow_html=True)

        # --- 2. TARGET ATOZ DOSSIER ---
        st.markdown('<div class="white-module">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">Target Intelligence Profile</div>', unsafe_allow_html=True)
        d1, d2 = st.columns(2)
        with d1:
            st.write(f"**Entity Name:** {data['target']['name']}")
            st.write(f"**Industry Vertical:** {data['target']['industry']}")
            st.write(f"**Operational Scope:** {data['target']['location']}")
            st.write(f"**Legal Framework:** {data['target']['risk']}")
        with d2:
            st.write(f"**Services They Offer:** {', '.join(data['target']['offers']) if data['target']['offers'] else 'Enterprise Solutions'}")
            st.write(f"**Internal Technology:** {', '.join(data['target']['tech']) if data['target']['tech'] else 'Custom Infrastructure'}")
            st.write(f"**Hiring Intensity:** {data['target']['hiring']}")
        st.markdown('</div>', unsafe_allow_html=True)

        # --- 3. SWOT & MARKET NEWS ---
        st.markdown('<div class="white-module">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">SWOT & Market Sentiment</div>', unsafe_allow_html=True)
        s1, s2 = st.columns(2)
        with s1:
            st.write(f"🟢 **[S] Strength:** Significant footprint in {data['target']['industry']} with a focus on {data['target']['hiring']}.")
            st.write(f"🔴 **[W] Weakness:** {data['target']['weakness']}.")
        with s2:
            st.write(f"🔵 **[O] Opportunity:** Transformation via {data['me']['services'][0]} to enhance {data['target']['weakness']} mitigation.")
            st.write(f"🟡 **[T] Threat:** Sector agile competitors scaling faster via modern frameworks.")
        st.divider()
        st.write("**Recent Intelligence Headlines:**")
        for n in data['target']['news']: st.write(f"• {n}")
        st.markdown('</div>', unsafe_allow_html=True)

        # --- 4. STAKEHOLDER RADAR ---
        st.markdown('<div class="white-module">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">LinkedIn Stakeholder Radar</div>', unsafe_allow_html=True)
        st.write("Target these Primary Decision Makers at **" + data['target']['name'] + "**:")
        roles = ["Chief Technology Officer", "VP Operations", "Head of Digital Strategy", "COO"]
        r_cols = st.columns(4)
        for i, r in enumerate(roles):
            with r_cols[i]:
                st.write(f"**{r}**")
                q = urllib.parse.quote(f"{data['target']['name']} {r}")
                st.markdown(f'<a href="https://www.linkedin.com/search/results/people/?keywords={q}" target="_blank" style="color:blue!important; text-decoration:underline;">🔍 View Names</a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # --- 5. THE PLAYBOOK (SCRIPTS) ---
        st.markdown('<div class="white-module">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">Sales Execution Playbook</div>', unsafe_allow_html=True)
        
        # Email
        st.write("**📧 Professional Email Pitch**")
        st.write("*Eyecatching Subject:* `Strategy: Unlocking {data['target']['name']}'s Growth Potential`")
        st.markdown(f"""<div class="script-block">
        "Hi [Name], I noticed {data['target']['name']}'s strong focus on <b>{data['target']['hiring']}</b> within the {data['target']['industry']} sector. <br><br>
        However, firms scaling rapidly often encounter bottlenecks, particularly with <b>{data['target']['weakness']}</b>. <br>
        At <b>{data['me']['name']}</b>, we specialize in <b>{data['me']['services'][0]}</b>, helping leaders like you transform these challenges into strategic advantages. <br><br>
        Would you be open to a brief chat next Tuesday to explore how we've achieved 15% efficiency gains for similar organizations?"
        </div>""", unsafe_allow_html=True)

        # Calling
        st.divider()
        st.write("**☎️ Tele-Calling & Voicemail**")
        st.markdown(f"""<div class="script-block">
        <b>Phone Script:</b> "Hi [Name], it's [YourName] from {data['me']['name']}. I'm calling because I noticed {data['target']['name']}'s impressive <b>{data['target']['hiring']}</b> and wanted to share a quick insight. <br>
        Most VPs in {data['target']['industry']} tell me their biggest hurdle during this growth is <b>{data['target']['weakness']}</b>. We've developed a framework that has helped similar companies overcome this. Do you have 2 minutes?"
        </div>""", unsafe_allow_html=True)
        st.write("*Voicemail Hook:*")
        st.code(f"Hi [Name], it's [YourName] from {data['me']['name']}. I have a specific insight regarding {data['target']['name']}'s {data['target']['weakness']} and its impact on your 2026 goals. I'll follow up with an email under the subject: {data['target']['name']} Strategic Growth.")

        # Improvisation
        st.divider()
        st.write("**🎯 Custom Personalization Hooks**")
        st.write(f"1. 'I saw {data['target']['name']} was recently mentioned in the news regarding: {data['target']['news'][0][:50]}...'")
        st.write(f"2. 'Given your current use of {data['target']['tech'][0] if data['target']['tech'] else 'your core digital stack'}, I thought this {data['me']['services'][0]} optimization map would be relevant.'")
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.error("Audit failed. Ensure URLs are reachable and valid.")
