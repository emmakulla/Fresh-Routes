import streamlit as st
from datetime import datetime
import requests
from modules.nav import SideBarLinks
from modules.driver_chat_utils import load_chats, save_chats

st.set_page_config(layout="wide")
SideBarLinks()

st.title("📦 Your Orders")

# ------------------ Fake Orders ------------------
orders = [
    {"orderID": 1, "status": "cancelled", "deliveryAddress": "61 Main St"},
    {"orderID": 2, "status": "out_for_delivery", "deliveryAddress": "50 Maple Dr"},
    {"orderID": 3, "status": "preparing", "deliveryAddress": "11 Walnut Ct"},
]

for o in orders:
    st.write(f"**Order ID:** {o['orderID']}  |  **Status:** {o['status']}  |  **Delivery:** {o['deliveryAddress']}")

    new_status = st.selectbox(
        f"Update status for order {o['orderID']}",
        ["pending", "preparing", "confirmed", "out_for_delivery", "delivered", "cancelled"],
        index=["pending", "preparing", "confirmed", "out_for_delivery", "delivered", "cancelled"].index(o["status"]),
        key=f"status_{o['orderID']}"
    )

    if st.button("Update Status", key=f"btn_{o['orderID']}"):
        o["status"] = new_status
        st.success(f"Order {o['orderID']} status updated to {new_status}!")

st.markdown("---")

# ------------------ Chat with Admin ------------------
st.header("💬 Chat with Admin")
driver_name = "DriverName1"

# Load chats safely
driver_chats = load_chats()
if not isinstance(driver_chats, dict):
    driver_chats = {}

drivers_dict = driver_chats.get("drivers", {})
if not isinstance(drivers_dict, dict):
    drivers_dict = {}
driver_chats["drivers"] = drivers_dict

driver_chats["drivers"].setdefault(driver_name, {})
driver_driver_orders = driver_chats["drivers"][driver_name]

# Pick first order for simplicity
order_id = "order_id_1"
driver_driver_orders.setdefault(order_id, [])

# Display chat history
for msg in driver_driver_orders[order_id]:
    if msg["from"] == "driver":
        st.markdown(f"**You:** {msg['message']} ({msg.get('timestamp', '')})")
    else:
        st.markdown(f"<div style='color: #1e88e5'><b>Admin:</b> {msg['message']} ({msg.get('timestamp', '')})</div>",
                    unsafe_allow_html=True)

# Send new message
with st.form("send_msg_form"):
    content = st.text_area("Message to Admin")
    submitted = st.form_submit_button("Send")
    if submitted and content.strip():
        driver_driver_orders[order_id].append({
            "from": "driver",
            "message": content.strip(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        save_chats(driver_chats)
        st.experimental_rerun()

st.markdown("---")

# ------------------ Traffic Updates (from API) ------------------
st.header("🚦 Traffic Updates")
API_URL = "http://web-api:4000/d"
driverID = 1  # Make sure this matches the API driverID

try:
    traffic_resp = requests.get(f"{API_URL}/driver/{driverID}/traffic")
    traffic_resp.raise_for_status()
    traffic = traffic_resp.json()
except Exception as e:
    st.error(f"Could not load traffic: {e}")
    traffic = []

if traffic:
    for t in traffic:
        st.write(f"Timestamp: {t.get('timestamp', '')}")
        st.write(f"Traffic Level: {t.get('trafficLevels', '')}")
        if t.get("notification"):
            st.info(f"Notification: {t['notification']}")
else:
    st.info("No traffic updates available.")
