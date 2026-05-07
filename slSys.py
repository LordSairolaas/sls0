import hashlib
import json
import os
import time
import streamlit as st
import pandas as pd

# --- المحرك الأساسي للنظام (The Blockchain Engine) ---
class SlsChain:
    def __init__(self, storage_folder="DAO_Warehouse"):
        self.storage_folder = storage_folder
        self.balances = {"System": 1000000, "Admin": 5000}
        
        if not os.path.exists(self.storage_folder):
            os.makedirs(self.storage_folder)
            self.create_genesis()
        
        self.load_and_sync()

    def calc_hash(self, block_data):
        """ حساب البصمة الرقمية للبيانات (SHA-256) """
        # نقوم بحذف الهاش القديم من البيانات قبل الحساب لضمان الدقة
        clean_data = {k: v for k, v in block_data.items() if k != 'hash'}
        payload = json.dumps(clean_data, sort_keys=True).encode()
        return hashlib.sha256(payload).hexdigest()

    def create_genesis(self):
        """ إنشاء الكتلة رقم 0 (بداية النظام) """
        genesis_tx = {
            "index": 0,
            "timestamp": time.time(),
            "sender": "World",
            "receiver": "System",
            "amount": 1000000,
            "asset_id": "GENESIS_ASSET",
            "prev_hash": "0"
        }
        genesis_tx["hash"] = self.calc_hash(genesis_tx)
        self.save_block_to_disk(genesis_tx)

    def save_block_to_disk(self, block_data):
        """ تخزين الكتلة كملف JSON مستقل (Chunking) """
        filename = f"block_{block_data['index']:05d}.json"
        path = os.path.join(self.storage_folder, filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(block_data, f, indent=4, ensure_ascii=False)

    def load_and_sync(self):
        """ قراءة كافة الملفات لتحديث الأرصدة وآخر هاش في الذاكرة """
        self.balances = {"System": 0} # إعادة تصوير الأرصدة بناءً على التاريخ المكتوب
        files = sorted([f for f in os.listdir(self.storage_folder) if f.endswith('.json')])
        self.chain_data = []
        
        for file in files:
            with open(os.path.join(self.storage_folder, file), 'r') as f:
                block = json.load(f)
                self.chain_data.append(block)
                # تحديث الأرصدة
                s, r, amt = block['sender'], block['receiver'], block['amount']
                if s != "World": self.balances[s] = self.balances.get(s, 0) - amt
                self.balances[r] = self.balances.get(r, 0) + amt
                self.last_block = block

    def add_new_block(self, sender, receiver, amount, asset_id):
        """ إضافة معاملة جديدة (كتلة جديدة) """
        if self.balances.get(sender, 0) < amount:
            return False, "❌ عذراً: الرصيد غير كافٍ لإتمام العملية."
        
        new_block = {
            "index": self.last_block['index'] + 1,
            "timestamp": time.time(),
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "asset_id": asset_id,
            "prev_hash": self.last_block['hash']
        }
        new_block["hash"] = self.calc_hash(new_block)
        self.save_block_to_disk(new_block)
        self.load_and_sync() # تحديث الحالة فوراً
        return True, "✅ تم تسجيل الكتلة في المخزن بنجاح."

# --- واجهة Streamlit (The UI) ---
def run_ui():
    st.set_page_config(page_title="SLS Chain Explorer", layout="wide")
    
    # تحسين المظهر
    st.title("🛡️ SLS DAO: Blockchain Explorer")
    st.markdown("نظام تخزين كتل البيانات (JSON Chunks) مع إدارة الأصول والأرصدة.")

    if 'dao' not in st.session_state:
        st.session_state.dao = SlsChain()

    dao = st.session_state.dao

    # --- القائمة الجانبية ---
    st.sidebar.header("📊 التحكم في الشبكة")
    action = st.sidebar.selectbox("اختر الإجراء:", ["عرض السلسلة الكاملة", "إضافة معاملة جديدة", "الأرصدة والأصول"])

    if action == "عرض السلسلة الكاملة":
        st.subheader("🔗 سلسلة الكتل (Blocks Log)")
        # عرض الكتل بشكل جمالي
        for block in reversed(dao.chain_data): # عرض الأحدث أولاً
            with st.expander(f"📦 Block #{block['index']} | Hash: {block['hash'][:12]}..."):
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**من:** {block['sender']}")
                    st.write(f"**إلى:** {block['receiver']}")
                    st.write(f"**الكمية:** {block['amount']} SLS")
                with c2:
                    st.write(f"**الأصل المرتبط:** {block['asset_id']}")
                    st.write(f"**الهاش السابق:** `{block['prev_hash'][:16]}...`")
                    st.caption(f"توقيت التسجيل: {time.ctime(block['timestamp'])}")
                st.json(block) # عرض الكود الخام للمبرمجين

    elif action == "إضافة معاملة جديدة":
        st.subheader("🖋️ تسجيل أصل/معاملة جديدة")
        with st.form("tx_form"):
            sender = st.selectbox("المرسل (عضو DAO):", list(dao.balances.keys()))
            receiver = st.text_input("المستلم (اسم العضو أو معرف المحفظة):")
            amount = st.number_input("قيمة المعاملة (Coins):", min_value=0.1)
            asset = st.text_input("معرف الأصل الحقيقي (مثل: العقار رقم 50):")
            
            if st.form_submit_button("توقيع وإرسال"):
                if not receiver or not asset:
                    st.warning("يرجى ملء كافة البيانات")
                else:
                    success, msg = dao.add_new_block(sender, receiver, amount, asset)
                    if success: 
                        st.success(msg)
                        st.balloons()
                    else: st.error(msg)

    elif action == "الأرصدة والأصول":
        st.subheader("🏦 سجل الأرصدة والأصول الحقيقية")
        df_bal = pd.DataFrame(dao.balances.items(), columns=["العضو", "الرصيد الحالي"])
        st.dataframe(df_bal, use_container_width=True)
        
        st.info("💡 ملاحظة: الأرصدة تُحسب ديناميكياً من خلال قراءة كافة ملفات الـ JSON في المجلد.")

if __name__ == "__main__":
    run_ui()
