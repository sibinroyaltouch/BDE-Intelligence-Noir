import subprocess
import sys

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

# --- 2. THE NOIR DESIGN SYSTEM (Strict Black & White) ---
st.set_page_config(page_title="Strategic ABI Noir", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    
    /* Global App Background */
    .stApp {
        background-color: #000000 !important;
        font-family: 'Inter', sans-serif;
    }

    /* Outer Headings (Outside White Boxes) */
    .main-title {
        text-align: center; 
        letter-spacing: 12px; 
        font-weight: 900; 
        color: #FFFFFF !important;
        margin-bottom: 5px;
    }
    .main-subtitle {
        text-align: center; 
        color: #888888 !important; 
        font-size: 0.9rem;
        margin-bottom: 40px;
    }

    /* Main Submit Button: White background, Black text */
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
        transition: 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #CCCCCC !important;
    }

    /* Input boxes */
    .stTextInput>div>div>input {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border: 1px solid #FFFFFF !important;
    }

    /* White Module Containers (Black Text Only) */
    .white-module {
        background-color: #FFFFFF !important;
        padding: 45px;
        border-radius: 0px;
        margin-bottom: 40px;
    }
    
    /* Force ALL text inside white modules to Black */
    .white-module h1, .white-module h2, .white-module h3, 
    .white-module h4, .white-module p, .white-module li, 
    .white-module span, .white-module div, .white-module b {
        color: #000000 !important;
    }

    .module-title {
        font-size: 1.8rem;
        font-weight: 900;
        text-transform: uppercase;
        border-bottom: 3px solid #000000;
        padding-bottom: 10px;
        margin-bottom: 30px;
    }

    /* KPI Bar - High Contrast White with Black Text */
    .kpi-container {
        display: flex;
        justify-content: space-around;
        background-color: #FFFFFF !important;
        padding: 35px;
        margin-bottom: 40px;
        text-align: center;
        border: 1px solid #FFFFFF;
    }
    .kpi-item h4 { 
        color: #000000 !important; 
        font-size: 0.75rem !important; 
        font-weight: 700 !important;
        letter-spacing: 2px; 
        margin-bottom: 5px;
        text-transform: uppercase;
    }
    .kpi-item h2 { 
        color: #000000 !important; 
        font-size: 2.2rem !important; 
        font-weight: 900 !important; 
        margin: 0; 
    }

    /* Code/Script blocks inside White Modules */
    .script-block {
        background-color: #F5F5F5;
        border: 1px solid #000000;
        padding: 25px;
        font-family: 'Courier New', monospace;
        color: #000000 !important;
        font-weight: 500;
        margin-bottom: 15px;
    }

    /* Alignment */
    .block-container { max-width: 1200px; padding-top: 3rem; margin: auto; }
    
    /* Remove default Streamlit shadows/padding */
    div[data-testid="stVerticalBlock"] > div { background: transparent; }
    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. THE ABI INTELLIGENCE ENGINE ---
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
        url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
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
        my_offer_keys = {
            "Cloud Transformation": ["aws", "cloud", "azure", "devops"],
            "AI/Automation Intelligence": ["ai", "machine learning", "automation"],
            "Cybersecurity & Compliance": ["security", "encryption", "soc", "compliance"],
            "Sales Tech Acceleration": ["salesforce", "hubspot", "crm", "pipeline"]
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
        if "platform" in t_data['text'] or "saas" in t_data['text']: target_offers.append("Digital Platform Solutions")
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
                "location": "Global",
                "risk": "GDPR / Strict" if ".uk" in self.target_url or ".de" in self.target_url else "CCPA / Moderate"
            },
            "me": {"name": self.my_url.split('.')[1].capitalize(), "services": my_strengths}
        }

# --- 4. DASHBOARD FRONTEND ---

st.markdown("<h1 class='main-title'>Sibin APP V 2.O</h1>", unsafe_allow_html=True)
st.markdown("<p class='main-subtitle'>Enterprise Strategic Intelligence • Strategic War Room Dossier</p>", unsafe_allow_html=True)

# Dual Inputs
col_a, col_b = st.columns(2)
with col_a: t_url = st.text_input("TARGET COMPANY URL (e.g. apple.com)", placeholder="Enter Prospect URL")
with col_b: m_url = st.text_input("YOUR COMPANY URL (e.g. salesforce.com)", value="https://")

if st.button("Execute Strategic Audit"):
    engine = TitanIntelligence(t_url, m_url)
    with st.spinner("INITIATING DEEP SCAN..."):
        data = engine.analyze()
    
    if data:
        # --- TOP KPI BAR (WHITE BACKGROUND / BLACK TEXT) ---
        st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-item"><h4>Lead Status</h4><h2>High</h2></div>
                <div class="kpi-item"><h4>Target Name</h4><h2>{data['target']['name']}</h2></div>
                <div class="kpi-item"><h4>Industry</h4><h2>{data['target']['industry']}</h2></div>
                <div class="kpi-item"><h4>Risk Profile</h4><h2>{data['target']['risk'].split()[0]}</h2></div>
            </div>
        """, unsafe_allow_html=True)

        # --- 1. THE STRATEGIC BRIDGE ---
        st.markdown(f"""
            <div class="white-module">
                <div class="module-title">Strategic Bridge: {data['me']['name']} → {data['target']['name']}</div>
                <p><b>Business Audit:</b> {data['target']['name']} is currently hiring for <b>{data['target']['hiring']}</b> but their infrastructure suggests a bottleneck in <b>{data['target']['weakness']}</b>.</p>
                <p><b>Solution Alignment:</b> As <b>{data['me']['name']}</b> is an expert in <b>{data['me']['services'][0]}</b>, we provide the specific tools needed to bypass their current weakness.</p>
                <p><b>The Wedge:</b> Pitch a cost-saving audit for {data['me']['services'][0]} to solve the {data['target']['weakness']} gap.</p>
            </div>
        """, unsafe_allow_html=True)

        # --- 2. ATOZ TARGET DOSSIER ---
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
            st.write(f"🟢 **[S] Strength:** Significant footprint in {data['target']['industry']}.")
            st.write(f"🔴 **[W] Weakness:** {data['target']['weakness']}.")
        with s2:
            st.write(f"🔵 **[O] Opportunity:** Transformation via {data['me']['services'][0]}.")
            st.write(f"🟡 **[T] Threat:** Sector agile competitors scaling faster.")
        st.divider()
        st.write("**Recent Intelligence Headlines:**")
        for n in data['target']['news']: st.write(f"• {n}")
        st.markdown('</div>', unsafe_allow_html=True)

        # --- 4. STAKEHOLDER RADAR ---
        st.markdown('<div class="white-module">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">LinkedIn Stakeholder Radar</div>', unsafe_allow_html=True)
        st.write("Target these Primary Decision Makers at **" + data['target']['name'] + "**:")
        roles = ["Chief Technology Officer", "VP Operations", "Head of Digital", "COO"]
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
        st.write("**📧 Professional Hookline Studio**")
        subject = f"Question regarding {data['target']['name']}'s focus on {data['target']['hiring'].split()[0]} growth"
        st.write(f"Subject: `{subject}`")
        st.markdown(f"""<div class="script-block">
        "Hi [Name], I noticed {data['target']['name']}'s recent footprint in {data['target']['industry']}.<br><br>
        Usually, when firms scale during <b>{data['target']['hiring']}</b> while leveraging <b>{data['target']['tech'][0] if data['target']['tech'] else 'their current stack'}</b>, 
        friction appears in <b>{data['target']['weakness']}</b>. <br><br>
        At <b>{data['me']['name']}</b>, we've helped similar firms bridge this specific gap. Do you have 2 minutes to chat next Tuesday?"
        </div>""", unsafe_allow_html=True)

        # Calling
        st.divider()
        st.write("**☎️ Tele-Calling & Voicemail**")
        st.markdown(f"""<div class="script-block">
        <b>Phone Script:</b> "Hi [Name], it's [YourName] from {data['me']['name']}. I'm calling because I noticed you're scaling your team. 
        Most VPs I talk to say their biggest hurdle during this growth phase is <b>{data['target']['weakness']}</b>. We've solved this for [Competitor]. Do you have a moment?"
        </div>""", unsafe_allow_html=True)
        st.write("*Voicemail Hook:*")
        st.code(f"Hi [Name], I have a specific insight regarding {data['target']['name']}'s {data['target']['weakness']} and its impact on your 2026 goals. I'll follow up with an email under the subject: {data['target']['name']} Strategy.")
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.error("Audit failed. Ensure URLs are reachable and valid.")
