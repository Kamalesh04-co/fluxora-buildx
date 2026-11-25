import streamlit as st
import requests
import json
import os

from config import OLLAMA_MODEL, OLLAMA_URL, firebase_login
from database import load_db, save_db, add_blockchain_record
from news_agent import get_live_maritime_and_political_news

st.set_page_config(page_title="Fluxora Maritime Command", page_icon="🚢", layout="wide")

# Load external UI stylesheet
def load_css(file_name: str = "style.css"):
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.role = None

if "live_news_feed" not in st.session_state:
    st.session_state.live_news_feed = "ALERT: Port of Rotterdam experiencing 36-hr dockworker strike. Suez route congestion up by 40%."

# ==========================================
# LOGIN SCREEN
# ==========================================
if not st.session_state.user:
    st.title("🚢 Fluxora - Autonomous Maritime Supply Chain")
    st.subheader("🔐 Firebase Role-Based Authentication")

    col1, col2 = st.columns([1, 1])
    with col1:
        role_choice = st.radio("Select Access Portal:", ["Captain Portal", "Port Authority Portal"])
        email = st.text_input(
            "Email ID",
            value="captain@fluxora.com" if role_choice == "Captain Portal" else "authority@fluxora.com"
        )
        password = st.text_input("Password", type="password", value="123456")

        if st.button("Login with Firebase", type="primary"):
            ok, msg = firebase_login(email, password)
            if ok:
                if "authority" in email.lower() or role_choice == "Port Authority Portal":
                    st.session_state.role = "Authority"
                else:
                    st.session_state.role = "Captain"
                st.session_state.user = email
                st.rerun()
            else:
                st.error(msg)
    st.stop()

# ==========================================
# HEADER & LOGOUT
# ==========================================
db = load_db()
top1, top2 = st.columns([5, 1])
with top1:
    st.title(f"🚢 Fluxora Command Center | {st.session_state.role} View")
    st.caption(f"Logged in as: {st.session_state.user}")
with top2:
    if st.button("🚪 Logout"):
        st.session_state.user = None
        st.session_state.role = None
        st.rerun()

st.divider()

# ==============================================================================
# CAPTAIN DASHBOARD
# ==============================================================================
if st.session_state.role == "Captain":
    tabs = st.tabs([
        "🌦️ 1. Telemetry & Ship Condition",
        "🤖 2. AI Scenario Planning",
        "📞 3. Port Contacts",
        "⚓ 4. Available Dock Spaces",
        "📊 5. Scenario Reasoning Matrix",
        "📨 6. Send Request to Authority",
        "⛓️ 7. Blockchain Status"
    ])

    # --- TAB 1: Telemetry & Live News ---
    with tabs[0]:
        st.header("🌦️ Disruption Sensing & Live Ship Telemetry")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🌊 External Environment & Live News")
            vessel_id = st.text_input("Vessel ID", "FLX-904")
            weather = st.selectbox("Live Weather Alert", [
                "Cyclone Warning - Bay of Bengal (Severity 8/10)",
                "Heavy Monsoon Swell (Severity 6/10)",
                "Clear Skies"
            ])

            news_region = st.text_input("Maritime Region for Live Search", "Indian Ocean, Bay of Bengal, Cochin, Colombo, Red Sea")
            if st.button("🌐 Fetch Live Maritime & Political News (100% Free RSS)"):
                with st.spinner("Fetching Google News and summarizing with Local AI..."):
                    st.session_state.live_news_feed = get_live_maritime_and_political_news(news_region)
                    st.rerun()

            live_news = st.text_area("Live Maritime & Political News Feed", value=st.session_state.live_news_feed, height=160)
            st.session_state.live_news_feed = live_news
            ambient_temp = st.number_input("External Sea/Air Temperature (°C)", value=31.5)

        with c2:
            st.subheader("🛳️ Internal Ship Condition")
            ship_temp = st.number_input("Cold-Chain Cargo / Engine Temp (°C)", value=-18.2)
            fuel = st.slider("Fuel Level (%)", 0, 100, 64)
            water = st.slider("Fresh Water Reserve (%)", 0, 100, 72)
            food = st.slider("Food & Rations Supply (Days Left)", 1, 60, 18)
            emp_cond = st.selectbox("Employee / Crew Condition", [
                "All Healthy & Active",
                "Minor Fatigue (2 Crew)",
                "Medical Attention Needed"
            ])

        st.session_state.ship_telemetry = {
            "vessel_id": vessel_id, "weather": weather, "news": live_news,
            "ambient_temp": ambient_temp, "ship_temp": ship_temp,
            "fuel": fuel, "water": water, "food": food, "crew": emp_cond
        }

    # --- TAB 2: AI Scenario Planning ---
    with tabs[1]:
        st.header("🤖 AI Agent: 3 Ranked Rerouting Scenarios")
        tel = st.session_state.get("ship_telemetry", {})
        ports_summary = json.dumps(db["ports"])

        if st.button("🚀 Run AI Scenario Planner", type="primary"):
            prompt = f"""
            You are Fluxora, an autonomous maritime AI agent.
            Ship Telemetry & Live Geopolitical/Maritime News: {json.dumps(tel)}
            Available Ports Data: {ports_summary}

            Generate 3 ranked rerouting scenarios (Rank 1, Rank 2, Rank 3) considering the live news, political climate, weather, and ship telemetry.
            For EACH scenario, clearly evaluate and list:
            - Route & Target Port
            - Estimated Time (ETA)
            - Price / Fuel Cost
            - Safety Score (/100)
            - Port Taxes
            - Estimated Profit / Loss ($)
            - Customer Comfort / Satisfaction (%)
            - Document Verification Time (Hours)
            """
            with st.spinner("Local AI Agent analyzing routes, taxes, profit/loss & safety..."):
                try:
                    res = requests.post(
                        OLLAMA_URL,
                        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": True},
                        stream=True
                    )
                    def stream_gen():
                        full_text = ""
                        for line in res.iter_lines():
                            if line:
                                chunk = json.loads(line).get("response", "")
                                full_text += chunk
                                yield chunk
                        st.session_state.ai_scenarios = full_text

                    st.write_stream(stream_gen)
                except Exception as e:
                    st.error(f"Ollama Connection Error: {e}")

        if "ai_scenarios" in st.session_state:
            st.info("AI Scenarios Generated! Check Tab 5 for the Reasoning Matrix or Tab 6 to submit your choice.")

    # --- TAB 3: Port Contacts ---
    with tabs[2]:
        st.header("📞 Port Authority Contacts (Live from Authorities)")
        for p in db["ports"]:
            with st.container(border=True):
                st.subheader(p["port_name"])
                st.write(f"**Contact:** {p['contact']}")
                st.write(f"**Port Details:** {p['port_details']}")
                st.write(f"**Required Documents:** {p['required_docs']}")

    # --- TAB 4: Available Dock Spaces ---
    with tabs[3]:
        st.header("⚓ Live Port Berth Availability (Excluding Fluxora Pre-Bookings)")
        for p in db["ports"]:
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Port", p["port_name"])
            col_b.metric("Pre-Booked via Fluxora", f"{p['pre_booked']} / {p['total_berths']}")
            col_c.metric("Available Ship Spaces Now", f"{p['available_spaces']} Spaces")
            st.divider()

    # --- TAB 5: Scenario Reasoning Matrix ---
    with tabs[4]:
        st.header("📊 Multi-Variable Decision & Reasoning Matrix")
        matrix_data = [
            {"Factor": "⏱️ Time (ETA)", "Rank 1 (Port of Cochin)": "38 hrs (-14 hrs saved)", "Rank 2 (Port of Colombo)": "46 hrs (-6 hrs saved)", "Rank 3 (Hold & Wait)": "68 hrs (+16 hrs delay)"},
            {"Factor": "💰 Price / Fuel Cost", "Rank 1 (Port of Cochin)": "$42,000", "Rank 2 (Port of Colombo)": "$48,500", "Rank 3 (Hold & Wait)": "$55,000"},
            {"Factor": "🛡️ Safety Score", "Rank 1 (Port of Cochin)": "94% (Out of Cyclone)", "Rank 2 (Port of Colombo)": "86% (Moderate Swell)", "Rank 3 (Hold & Wait)": "61% (High Storm Risk)"},
            {"Factor": "🏛️ Port Taxes", "Rank 1 (Port of Cochin)": "$3,200", "Rank 2 (Port of Colombo)": "$4,100", "Rank 3 (Hold & Wait)": "$1,500"},
            {"Factor": "📈 Profit / Loss Impact", "Rank 1 (Port of Cochin)": "+$18,400 Net Profit", "Rank 2 (Port of Colombo)": "+$9,200 Net Profit", "Rank 3 (Hold & Wait)": "-$14,000 Loss"},
            {"Factor": "😊 Customer Comfort %", "Rank 1 (Port of Cochin)": "96% (Cold-Chain Safe)", "Rank 2 (Port of Colombo)": "89%", "Rank 3 (Hold & Wait)": "64% (Spoilage Risk)"},
            {"Factor": "📄 Doc Verification Time", "Rank 1 (Port of Cochin)": "45 Mins (Fluxora Fast-Track)", "Rank 2 (Port of Colombo)": "2 Hours", "Rank 3 (Hold & Wait)": "N/A"}
        ]
        st.table(matrix_data)
        if "ai_scenarios" in st.session_state:
            st.subheader("Detailed AI Explanation:")
            st.markdown(st.session_state.ai_scenarios)

    # --- TAB 6: Send Request to Authority ---
    with tabs[5]:
        st.header("📨 Submit Reroute Decision & Ship Documents to Port Authority")
        target_port = st.selectbox("Select Target Port", [p["port_name"] for p in db["ports"]])
        chosen_scenario = st.selectbox("Chosen AI Scenario", ["Rank 1 - Immediate Divert", "Rank 2 - Alternate Hub", "Rank 3 - Emergency Hold"])
        captain_note = st.text_area("Message to Port Authority", "Requesting priority berth allocation due to cyclone warning. Cold-chain cargo intact.")
        uploaded_docs = st.file_uploader("Upload Ship Documents (Manifest, Customs, Health Cert)", accept_multiple_files=True)

        if st.button("⛓️ Sign & Send Request via Blockchain", type="primary"):
            doc_names = [f.name for f in uploaded_docs] if uploaded_docs else ["Standard_Fluxora_Digital_Manifest.pdf"]
            tel = st.session_state.get("ship_telemetry", {"vessel_id": "FLX-904"})

            req_id = f"REQ-{len(db['requests']) + 101}"
            new_req = {
                "req_id": req_id,
                "vessel_id": tel.get("vessel_id", "FLX-904"),
                "captain": st.session_state.user,
                "target_port": target_port,
                "scenario": chosen_scenario,
                "ship_condition": tel,
                "documents": doc_names,
                "message": captain_note,
                "status": "Pending Authority Verification",
                "authority_remarks": ""
            }
            db["requests"].append(new_req)
            add_blockchain_record(db, "CAPTAIN_REROUTE_REQUEST", f"{req_id} -> {target_port} ({chosen_scenario})")
            save_db(db)
            st.success(f"Request {req_id} sent to {target_port} & recorded on Blockchain!")

    # --- TAB 7: Blockchain Status ---
    with tabs[6]:
        st.header("⛓️ Authority Decisions & Immutable Blockchain Log")
        for r in reversed(db["requests"]):
            with st.container(border=True):
                st.write(f"**{r['req_id']}** | Target: **{r['target_port']}** | Status: **{r['status']}**")
                if r["authority_remarks"]:
                    st.info(f"Authority Message: {r['authority_remarks']}")

        st.subheader("🔗 Cryptographic Ledger")
        for b in reversed(db["blockchain"]):
            st.code(f"Block #{b['block']} | {b['action']} | {b['details']}\nHash: {b['hash']}")

# ==============================================================================
# PORT AUTHORITY DASHBOARD
# ==============================================================================
elif st.session_state.role == "Authority":
    auth_tabs = st.tabs([
        "🏗️ 1. Upload Port Details & Spaces",
        "📞 2. Update Port Contacts",
        "📋 3. Incoming Ship Requests & Verification",
        "⛓️ 4. Blockchain Audit Trail"
    ])

    with auth_tabs[0]:
        st.header("🏗️ Manage Port Details & Ship Space Availability")
        port_names = [p["port_name"] for p in db["ports"]]
        selected_p = st.selectbox("Select Your Port", port_names)
        port_obj = next(p for p in db["ports"] if p["port_name"] == selected_p)

        total_b = st.number_input("Total Port Berths", value=port_obj["total_berths"])
        pre_b = st.number_input("Pre-Booked Ships (via Fluxora)", value=port_obj["pre_booked"])
        avail_b = max(0, total_b - pre_b)
        st.metric("Calculated Available Ship Spaces (Excluding Pre-Bookings)", f"{avail_b} Spaces")

        p_details = st.text_area("Port Infrastructure & Operational Details", value=port_obj["port_details"])
        req_docs = st.text_input("Required Documents from Incoming Ships", value=port_obj["required_docs"])

        if st.button("💾 Publish Port Availability", type="primary"):
            port_obj["total_berths"] = total_b
            port_obj["pre_booked"] = pre_b
            port_obj["available_spaces"] = avail_b
            port_obj["port_details"] = p_details
            port_obj["required_docs"] = req_docs
            save_db(db)
            st.success("Port Details & Live Available Spaces Updated for all Captains!")

    with auth_tabs[1]:
        st.header("📞 Port Authority Contact Details")
        selected_p2 = st.selectbox("Port", [p["port_name"] for p in db["ports"]], key="contact_port")
        port_obj2 = next(p for p in db["ports"] if p["port_name"] == selected_p2)
        new_contact = st.text_input("Official Emergency & Operations Contact", value=port_obj2["contact"])
        if st.button("Update Contact"):
            port_obj2["contact"] = new_contact
            save_db(db)
            st.success("Contact details updated!")

    with auth_tabs[2]:
        st.header("📋 Incoming Ship Requests, Telemetry & Document Verification")
        if not db["requests"]:
            st.info("No incoming ship requests yet.")
        for r in reversed(db["requests"]):
            with st.container(border=True):
                st.subheader(f"🚢 {r['req_id']} - Vessel: {r['vessel_id']} ➡️ {r['target_port']}")
                st.write(f"**Chosen Scenario:** {r['scenario']} | **Current Status:** `{r['status']}`")
                st.write(f"**Captain Message:** {r['message']}")

                col_x, col_y = st.columns(2)
                with col_x:
                    st.markdown("**📊 Incoming Ship Condition:**")
                    st.json(r["ship_condition"])
                with col_y:
                    st.markdown("**📄 Submitted Ship Documents:**")
                    for d in r["documents"]:
                        st.write(f"✅ {d}")

                remarks = st.text_input("Authority Verification Remarks", key=f"rem_{r['req_id']}", value="Documents verified. Berth #4 assigned.")
                b1, b2 = st.columns(2)
                if b1.button("✅ Approve & Send Decision", key=f"app_{r['req_id']}", type="primary"):
                    r["status"] = "APPROVED BY PORT AUTHORITY"
                    r["authority_remarks"] = remarks
                    add_blockchain_record(db, "AUTHORITY_APPROVED", f"{r['req_id']} Approved by {st.session_state.user}")
                    save_db(db)
                    st.rerun()
                if b2.button("❌ Reject Request", key=f"rej_{r['req_id']}"):
                    r["status"] = "REJECTED BY PORT AUTHORITY"
                    r["authority_remarks"] = remarks
                    add_blockchain_record(db, "AUTHORITY_REJECTED", f"{r['req_id']} Rejected by {st.session_state.user}")
                    save_db(db)
                    st.rerun()

    with auth_tabs[3]:
        st.header("⛓️ Blockchain Decision Ledger")
        for b in reversed(db["blockchain"]):
            st.code(f"Block #{b['block']} | {b['timestamp']} | {b['action']}\nDetails: {b['details']}\nHash: {b['hash']}")
