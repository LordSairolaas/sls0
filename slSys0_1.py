import hashlib, json, os, time, threading
import streamlit as st
import pandas as pd
import requests
from fastapi import FastAPI, Request
import uvicorn

# --- إعدادات المحرك (Engine) ---
class SlsNode:
    def __init__(self, node_id, storage_folder="DAO_Warehouse"):
        self.node_id = node_id
        self.storage_folder = storage_folder
        self.peers = set()
        if not os.path.exists(self.storage_folder): os.makedirs(self.storage_folder)
        self.sync_local_data()

    def calc_hash(self, data):
        # التأكد من حساب الهاش بدون حقل الهاش نفسه
        clean = {k: v for k, v in data.items() if k != 'hash'}
        return hashlib.sha256(json.dumps(clean, sort_keys=True).encode()).hexdigest()

    def save_block(self, block):
        path = os.path.join(self.storage_folder, f"block_{block['index']:05d}.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(block, f, indent=4, ensure_ascii=False)

    def sync_local_data(self):
        """ هذه الدالة التي كان فيها خطأ المسمى """
        self.chain = []
        self.balances = {"System": 1000000}
        files = sorted([f for f in os.listdir(self.storage_folder) if f.endswith('.json')])
        self.last_block = {"index": -1, "hash": "0"}
        
        for f in files:
            with open(os.path.join(self.storage_folder, f), 'r') as file:
                b = json.load(file)
                self.chain.append(b)
                s, r, amt = b['sender'], b['receiver'], b['amount']
                self.balances[s] = self.balances.get(s, 0) - amt
                self.balances[r] = self.balances.get(r, 0) + amt
                self.last_block = b

# --- إعدادات الشبكة (P2P API) ---
api = FastAPI()
node_engine = SlsNode(node_id="Master_Node") # العقدة المحلية

@api.post("/sync")
async def receive_sync(request: Request):
    """ استقبال الكتل من العقد الأخرى """
    new_block = await request.json()
    node_engine.save_block(new_block)
    return {"status": "ok"}

def run_api():
    # استخدام منفذ مختلف لتجنب الخطأ 10048
    try:
        uvicorn.run(api, host="0.0.0.0", port=8001)
    except:
        pass

# --- واجهة Streamlit ---
def main():
    st.set_page_config(page_title="SLS DAO Node", layout="wide")
    
    # بدء خادم الاستقبال في الخلفية (مرة واحدة فقط)
    if 'api_started' not in st.session_state:
        threading.Thread(target=run_api, daemon=True).start()
        st.session_state.api_started = True

    node = node_engine
    node.sync_local_data() # تحديث البيانات

    st.title(f"🖥️ DAO Node: {node.node_id}")

    tab1, tab2, tab3 = st.tabs(["🔗 السلسلة (Explorer)", "💸 معاملات", "🌐 الشبكة"])

    with tab1:
        for b in reversed(node.chain):
            with st.expander(f"Block #{b['index']} | Hash: {b['hash'][:10]}..."):
                st.json(b)

    with tab2:
        with st.form("tx"):
            sender = st.selectbox("المرسل:", list(node.balances.keys()))
            receiver = st.text_input("المستلم:")
            amt = st.number_input("الكمية:", min_value=1.0)
            asset = st.text_input("الأصل (RWA):")
            if st.form_submit_button("إرسال للشبكة"):
                new_b = {
                    "index": node.last_block['index'] + 1,
                    "timestamp": time.time(),
                    "sender": sender, "receiver": receiver,
                    "amount": amt, "asset_id": asset,
                    "prev_hash": node.last_block['hash']
                }
                new_b["hash"] = node.calc_hash(new_b)
                node.save_block(new_b)
                # نشر المعاملة للعقد الأخرى
                for peer in node.peers:
                    try: requests.post(f"{peer}/sync", json=new_b, timeout=1)
                    except: pass
                st.rerun()

    with tab3:
        p_ip = st.text_input("عنوان عقدة زميلة (مثال: http://192.168.1.10:8001)")
        if st.button("ربط"):
            node.peers.add(p_ip)
            st.success(f"تم الربط مع {p_ip}")

if __name__ == "__main__":
    main()
