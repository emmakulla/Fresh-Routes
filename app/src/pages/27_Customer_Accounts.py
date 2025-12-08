import streamlit as st
import requests
from modules.nav import SideBarLinks
from datetime import datetime

API = "http://localhost:4000"  # your API gateway

st.set_page_config(layout="wide")
SideBarLinks()

# ----------------- PAGE STYLE -----------------
st.markdown("""
<style>
.page-title {
    font-size: 2.4rem; 
    font-weight: 700; 
    margin-bottom: .5rem;
}
.sub {
    color: #444;
    margin-bottom: 1.5rem;
}

.customer-card {
    padding: 1rem 1rem;
    border-bottom: 1px solid #eee;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.customer-left {
    display: flex;
    flex-direction: column;
}

.customer-name {
    font-size: 1.2rem;
    font-weight: 700;
}

.customer-email {
    color: #777;
    margin-top: -2px;
}

.feedback-text {
    font-style: italic;
    color: #555;
    font-size: 1rem;
}

.btn-row {
    display: flex;
    gap: .5rem;
}

.reply-btn, .delete-btn {
    padding: .35rem 1rem;
    border-radius: 8px;
    cursor: pointer;
    font-size: .85rem;
    border: none;
}

.reply-btn {
    background: #e9e9e9;
}

.reply-btn:hover {
    background: #d8d8d8;
}

.delete-btn {
    background: #ffdddd;
}

.delete-btn:hover {
    background: #ffcccc;
}
</style>
""", unsafe_allow_html=True)

# ----------------- HEADER -----------------
st.markdown("""
<div class='page-title'>Customer Accounts + Feedback</div>
<div class='sub'>Active Customer Accounts</div>
""", unsafe_allow_html=True)


# ----------------- FETCH CUSTOMER LIST -----------------
def load_customers():
    try:
        r = requests.get(f"{API}/admin/customers")
        if r.status_code == 200:
            return r.json()
        else:
            st.error(f"Error loading customers: {r.text}")
            return []
    except Exception as e:
        st.error(f"Error: {e}")
        return []


customers = load_customers()


# ----------------- DISPLAY CUSTOMERS -----------------
for cust in customers:
    cust_id = cust["customerID"]
    full_name = f"{cust['firstName']} {cust['lastName']}"
    email = cust["email"]
    feedback = cust.get("latestFeedback", "No feedback yet")

    st.markdown("<div class='customer-card'>", unsafe_allow_html=True)

    # LEFT SIDE — NAME + EMAIL
    left, right = st.columns([4, 2])

    with left:
        st.markdown(f"""
        <div class='customer-left'>
            <div class='customer-name'>{full_name}</div>
            <div class='customer-email'>{email}</div>
        </div>
        """, unsafe_allow_html=True)

    # MIDDLE — FEEDBACK
    st.markdown(f"""
    <div class='feedback-text'>
        "{feedback}"
    </div>
    """, unsafe_allow_html=True)

    # RIGHT SIDE — BUTTONS
    with right:
        c1, c2 = st.columns([1, 1])

        # -------- Reply Button --------
        if c1.button("Reply", key=f"reply-{cust_id}", use_container_width=True):
            with st.modal(f"Reply to {full_name}"):
                st.subheader(f"Send Reply to {full_name}")
                msg = st.text_area("Message", height=120)

                if st.button("Send"):
                    message_id = int(datetime.now().timestamp()) % 2147483647
                    payload = {
                        "messageID": message_id,
                        "content": msg,
                        "timestamp": datetime.now().strftime("%Y-%m-%d")
                    }

                    res = requests.post(f"{API}/admin/customer/{cust_id}/customermessages", json=payload)
                    if res.status_code == 201:
                        st.success("Message sent!")
                    else:
                        st.error(f"Failed to send message: {res.text}")

        # -------- Delete Button --------
        if c2.button("Delete Account", key=f"del-{cust_id}", use_container_width=True):
            res = requests.delete(f"{API}/admin/customers/{cust_id}")
            if res.status_code == 200:
                st.success("Customer deleted!")
                st.rerun()
            else:
                st.error(f"Error deleting: {res.text}")

    st.markdown("</div>", unsafe_allow_html=True)
