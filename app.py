import streamlit as st
import hashlib
import time
import json

# إعدادات المنظومة العليا
st.set_page_config(page_title="Seraleesen Arts", layout="wide")

# =====================================================================
# 1. المحرك الزمني المطلق (Lordstire Absolute Temporal Engine)
# =====================================================================
class LordstireEngine:
    def __init__(self):
        # العهد: 1 يناير 2025
        self.EPOCH = 1735689600 
        self.SEC_IN_DAY = 86400

    def get_now(self):
        # حساب اللحظة الراهنة بناءً على الثواني المطلقة
        elapsed = time.time() - self.EPOCH
        total_days = int(elapsed // self.SEC_IN_DAY)
        
        # التقويم العشري
        year = (total_days // 1000) + 1
        rem_year = total_days % 1000
        month = (rem_year // 100) + 1
        rem_month = rem_year % 100
        week = (rem_month // 10) + 1
        day_in_week = (rem_month % 10) + 1
        day_in_month = rem_month + 1

        # الوقت العشري (10 ساعات)
        sec_today = elapsed % self.SEC_IN_DAY
        lt_hour = int(sec_today // 8640)
        rem_sec = sec_today % 8640
        lt_min = int(rem_sec // 86.4)
        lt_sec = int((rem_sec % 86.4) // 0.864)

        return {
            "stamp": f"LTS-{year:02d}.{month:02d}.{day_in_month:02d} | {lt_hour:01d}:{lt_min:02d}:{lt_sec:02d}",
            "day_total": total_days
        }

# =====================================================================
# 2. بلوكتشاين المنظومة (The Core Ledger)
# =====================================================================
class LordstireBlockchain:
    def __init__(self):
        if 'chain' not in st.session_state:
            # إنشاء كتلة التأسيس (Genesis Block)
            genesis_ts = "LTS-01.01.01 | 0:00:00"
            st.session_state.chain = [self._create_block(0, "Genesis: Seraleesen Arts Initiated", "0", genesis_ts)]

    def _create_block(self, index, data, prev_hash, timestamp):
        block_content = json.dumps({"idx": index, "data": data, "prev": prev_hash, "ts": timestamp}, sort_keys=True)
        block_hash = hashlib.sha256(block_content.encode()).hexdigest()
        return {"index": index, "data": data, "hash": block_hash, "prev_hash": prev_hash, "timestamp": timestamp}

    def record_event(self, event_data, timestamp):
        # إضافة سجل جديد للسلسلة
        prev_block = st.session_state.chain[-1]
        new_block = self._create_block(len(st.session_state.chain), event_data, prev_block['hash'], timestamp)
        st.session_state.chain.append(new_block)
        return new_block['hash']

# =====================================================================
# 3. واجهة المستخدم والتنظيم (UI & Sections)
# =====================================================================
def main():
    # استدعاء المحركات
    engine = LordstireEngine()
    ledger = LordstireBlockchain()
    current = engine.get_now()

    # القائمة الجانبية - المركز الزمني
    st.sidebar.title("Seraleesen Arts")
    st.sidebar.subheader("Temporal Identity")
    st.sidebar.metric("Lordstire Time", current['stamp'].split('|')[1])
    st.sidebar.info(f"📅 Date: {current['stamp'].split('|')[0]}")
    st.sidebar.caption(f"Chronological Day: {current['day_total']}")
    st.sidebar.divider()

    # أقسام الموقع المترابطة
    menu = [
        "Dashboard",
        "Management (Accountability)",
        "Warehouse (Treasury)",
        "Factory (Production)",
        "Store (Exchange)",
        "R&D (Archives)",
        "Campaigns & Camps",
        "System Ledger (Blockchain)"
    ]
    choice = st.sidebar.radio("Navigate System:", menu)

    st.title(f"Section: {choice}")
    st.markdown(f"**Verification Stamp:** `{current['stamp']}`")
    st.divider()

    # منطق الأقسام مع ربطها بالبلوكتشاين
    if choice == "Dashboard":
        st.header("Global Overview")
        col1, col2 = st.columns(2)
        col1.metric("Verified Operations", len(st.session_state.chain))
        col2.metric("System Integrity", "Locked (SHA-256)")
        st.write("Welcome to the decentralized hub of Lordstire.")

    elif choice == "Management (Accountability)":
        st.header("Identity & Registration")
        with st.form("reg_form"):
            entity_name = st.text_input("Entity/Project Name")
            action = st.selectbox("Action", ["Register Entity", "Update Status", "Assign Rank"])
            submit = st.form_submit_button("Authenticate & Record")
            
            if submit:
                log = f"MGMT: {action} for {entity_name}"
                h = ledger.record_event(log, current['stamp'])
                st.success(f"Operation Secured! Block Hash: {h[:16]}...")

    elif choice == "Warehouse (Treasury)":
        st.header("Inventory Ledger")
        # مثال على إضافة مخزون بازلتي
        with st.expander("Update Mineral Stock"):
            amount = st.number_input("Amount (Tons/Kg)", min_value=0.0)
            material = st.selectbox("Material", ["Basalt Rocks", "Silver Powder", "Silica", "Refined Alcohol"])
            if st.button("Seal Transaction"):
                log = f"TREASURY: Added {amount} of {material}"
                ledger.record_event(log, current['stamp'])
                st.toast("Treasury updated and hashed.")
        
        st.subheader("Current Stock Records")
        # استخراج البيانات من البلوكتشاين (المصدر الوحيد للحقيقة)
        warehouse_logs = [b for b in st.session_state.chain if "TREASURY" in b['data']]
        if warehouse_logs:
            st.table(warehouse_logs)
        else:
            st.write("No verified transactions found.")

    elif choice == "System Ledger (Blockchain)":
        st.header("Immutable Chain History")
        st.write("Every action in this site is a block in this chain.")
        for b in reversed(st.session_state.chain):
            with st.expander(f"Block #{b['index']} | Timestamp: {b['timestamp']}"):
                st.json(b)

    else:
        st.info(f"Module '{choice}' is active. All interactions here are auto-signed by the Lordstire Ledger.")

    # تحديث تلقائي للحفاظ على تزامن الوقت والبلوكتشاين
    time.sleep(1)
    st.rerun()

if __name__ == "__main__":
    main()
