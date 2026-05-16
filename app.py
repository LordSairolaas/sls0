import streamlit as st
import hashlib
import time
import json
import uuid
import pandas as pd
import base64
import os

# =====================================================================
# SYSTEM CONFIGURATION & STYLING
# =====================================================================
st.set_page_config(page_title="Seraleesen Arts Core OS", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stButton>button { border-radius: 6px; font-weight: bold; transition: 0.2s; width: 100%; }
    .comment-container { margin-left: 20px; padding-left: 10px; border-left: 2px solid #333; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 1. PERSISTENCE STORAGE HELPER
# =====================================================================
class FileStorageHelper:
    @staticmethod
    def load_json(filename: str, default_factory):
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return default_factory()
        return default_factory()

    @staticmethod
    def save_json(filename: str, data):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4, default=str)
        except Exception as e:
            st.error(f"Storage IO Error: {str(e)}")

# =====================================================================
# 2. TIME ENGINE CLASS (محرك الوقت والتقويم اللوردستايري العشري)
# =====================================================================
class LordstireTimeEngine:
    def __init__(self):
        self.EPOCH = 1735689600 
        self.SEC_IN_DAY = 86400

    def get_timestamp(self) -> str:
        elapsed = time.time() - self.EPOCH
        total_days = int(elapsed // self.SEC_IN_DAY)
        year = (total_days // 1000) + 1
        rem_year = total_days % 1000
        month = (rem_year // 100) + 1
        day_in_month = (rem_year % 100) + 1
        sec_today = elapsed % self.SEC_IN_DAY
        lt_hour = int(sec_today // 8640)
        lt_min = int((sec_today % 8640) // 86.4)
        lt_sec = int(((sec_today % 8640) % 86.4) // 0.864)
        return f"LTS-{year:04d}.{month:03d}.{day_in_month:03d} | {lt_hour:02d}:{lt_min:02d}:{lt_sec:02d}"

# =====================================================================
# 3. BLOCKCHAIN ENGINE CLASS (محرك الأمان والتأريخ البلوكتشاينى المتقدم)
# =====================================================================
class LordstireBlockchain:
    def __init__(self):
        self.file_path = "blockchain_ledger.json"
        if 'chain' not in st.session_state:
            st.session_state.chain = FileStorageHelper.load_json(self.file_path, list)
            if not st.session_state.chain:
                self.record_event("SYSTEM_BOOT", {"status": "Genesis Block Operational"}, "LTS-0001.001.001 | 00:00:00")

    def record_event(self, action_type: str, details_dict: dict, timestamp: str) -> str:
        prev_hash = st.session_state.chain[-1]['hash'] if st.session_state.chain else "0" * 64
        index = len(st.session_state.chain)
        
        payload = json.dumps({"action": action_type, "details": details_dict}, sort_keys=True, default=str)
        block_content = f"{index}{payload}{prev_hash}{timestamp}"
        block_hash = hashlib.sha256(block_content.encode()).hexdigest()
        
        block = {
            "index": index, "action": action_type, "details": details_dict, 
            "ts": timestamp, "hash": block_hash, "prev": prev_hash
        }
        st.session_state.chain.append(block)
        FileStorageHelper.save_json(self.file_path, st.session_state.chain)
        return block_hash

# =====================================================================
# 4. DATABASE MANAGER CLASS (إدارة قواعد البيانات والمزامنة مع الملفات المحلية)
# =====================================================================
class DatabaseManager:
    TARGETS = {
        'users_db': dict, 'inventory_db': dict, 'store_db': dict, 
        'campaigns_db': dict, 'posts_db': list, 'chat_db': list, 
        'dms_db': list, 'permissions_db': dict
    }

    @staticmethod
    def initialize():
        for db_name, factory in DatabaseManager.TARGETS.items():
            if db_name not in st.session_state:
                st.session_state[db_name] = FileStorageHelper.load_json(f"{db_name}.json", factory)
        
        if not st.session_state.permissions_db:
            st.session_state.permissions_db = {
                "Supreme Lord": {"edit_users": True, "view_blockchain": True, "edit_perms": True},
                "High Commander": {"edit_users": True, "view_blockchain": True, "edit_perms": False},
                "Initiate": {"edit_users": False, "view_blockchain": False, "edit_perms": False},
                "Contributor": {"edit_users": False, "view_blockchain": False, "edit_perms": False}
            }
            DatabaseManager.synchronize('permissions_db')

        if 'current_user' not in st.session_state: st.session_state.current_user = None

    @staticmethod
    def synchronize(db_name: str):
        if db_name in st.session_state:
            FileStorageHelper.save_json(f"{db_name}.json", st.session_state[db_name])

# =====================================================================
# 5. SOCIAL & INTERACTION ENGINE (محرك المنشورات والتفاعلات والرسائل الخاصة المتقدمة)
# =====================================================================
class SocialEngine:
    @staticmethod
    def add_post(author_id: str, author_name: str, text: str, file_obj, is_public: bool, timestamp: str, ledger: LordstireBlockchain):
        post_id = str(uuid.uuid4())
        file_data, file_meta = None, {}
        if file_obj is not None:
            file_data = base64.b64encode(file_obj.read()).decode('utf-8')
            file_meta = {"name": file_obj.name, "type": file_obj.type}
            
        post = {
            "post_id": post_id, "author_id": author_id, "author": author_name, "content": text,
            "file_data": file_data, "file_meta": file_meta, "ts": timestamp, "is_public": is_public,
            "reacts": {"⚡ Power": 0, "🪐 Cosmos": 0, "⚒️ Construct": 0}, "reacted_users": {},
            "comments": [], "is_repost": False, "original_author": None
        }
        st.session_state.posts_db.append(post)
        DatabaseManager.synchronize('posts_db')
        ledger.record_event("POST_CREATED", {"post_id": post_id, "author": author_name, "public": is_public}, timestamp)

    @staticmethod
    def add_comment(post_id: str, user_name: str, comment_text: str, file_obj, timestamp: str, ledger: LordstireBlockchain):
        for post in st.session_state.posts_db:
            if post["post_id"] == post_id:
                file_data, file_meta = None, {}
                if file_obj is not None:
                    file_data = base64.b64encode(file_obj.read()).decode('utf-8')
                    file_meta = {"name": file_obj.name, "type": file_obj.type}
                
                comment_obj = {
                    "comment_id": str(uuid.uuid4()), "author": user_name, "text": comment_text, 
                    "ts": timestamp, "file_data": file_data, "file_meta": file_meta
                }
                if "comments" not in post: post["comments"] = []
                post["comments"].append(comment_obj)
                DatabaseManager.synchronize('posts_db')
                ledger.record_event("POST_COMMENTED", {"post_id": post_id, "by": user_name}, timestamp)
                break

    @staticmethod
    def trigger_react(post_id: str, user_id: str, react_type: str, timestamp: str, ledger: LordstireBlockchain):
        for post in st.session_state.posts_db:
            if post["post_id"] == post_id:
                if "reacts" not in post or not isinstance(post["reacts"], dict):
                    post["reacts"] = {"⚡ Power": 0, "🪐 Cosmos": 0, "⚒️ Construct": 0}
                if "reacted_users" not in post: 
                    post["reacted_users"] = {}
                
                previous_react = post["reacted_users"].get(user_id)
                if previous_react == react_type:
                    post["reacts"][react_type] = max(0, post["reacts"].get(react_type, 1) - 1)
                    del post["reacted_users"][user_id]
                    action = "REACT_REMOVED"
                else:
                    if previous_react: 
                        post["reacts"][previous_react] = max(0, post["reacts"].get(previous_react, 1) - 1)
                    post["reacts"][react_type] = post["reacts"].get(react_type, 0) + 1
                    post["reacted_users"][user_id] = react_type
                    action = "REACT_ADDED"
                    
                DatabaseManager.synchronize('posts_db')
                ledger.record_event(action, {"post_id": post_id, "user_id": user_id, "type": react_type}, timestamp)
                break

    @staticmethod
    def share_repost(post_id: str, reposter_id: str, reposter_name: str, timestamp: str, ledger: LordstireBlockchain):
        for post in st.session_state.posts_db:
            if post["post_id"] == post_id:
                repost_obj = {
                    "post_id": str(uuid.uuid4()), "author_id": reposter_id, "author": reposter_name,
                    "content": post["content"], "file_data": post.get("file_data"), "file_meta": post.get("file_meta"),
                    "ts": timestamp, "is_public": post["is_public"], "reacts": {"⚡ Power": 0, "🪐 Cosmos": 0, "⚒️ Construct": 0},
                    "reacted_users": {}, "comments": [], "is_repost": True, "original_author": post["author"]
                }
                st.session_state.posts_db.append(repost_obj)
                DatabaseManager.synchronize('posts_db')
                ledger.record_event("POST_REPOSTED", {"original_id": post_id, "reposted_by": reposter_name}, timestamp)
                break

    @staticmethod
    def send_private_message(sender_id: str, sender_name: str, receiver_id: str, text: str, file_obj, timestamp: str, ledger: LordstireBlockchain):
        file_data, file_meta = None, {}
        if file_obj is not None:
            file_data = base64.b64encode(file_obj.read()).decode('utf-8')
            file_meta = {"name": file_obj.name, "type": file_obj.type}
            
        dm = {
            "dm_id": str(uuid.uuid4()), "sender_id": sender_id, "sender_name": sender_name, 
            "receiver_id": receiver_id, "text": text, "ts": timestamp,
            "file_data": file_data, "file_meta": file_meta
        }
        st.session_state.dms_db.append(dm)
        DatabaseManager.synchronize('dms_db')
        ledger.record_event("DM_TRANSMITTED", {"sender": sender_name, "receiver_id": receiver_id}, timestamp)

# =====================================================================
# 6. AUTHENTICATION & AUTHORITY ENGINE (إدارة الحسابات والصلاحيات)
# =====================================================================
class AuthManager:
    def __init__(self, time_engine: LordstireTimeEngine, ledger: LordstireBlockchain):
        self.time_engine = time_engine
        self.ledger = ledger

    def register(self, user_data: dict) -> dict:
        entity_id = str(uuid.uuid4())
        join_date = self.time_engine.get_timestamp()
        
        new_user = {
            "Id": entity_id, "name": user_data['name'], "title": user_data.get('title', 'Contributor'),
            "type": user_data.get('type', 'Saien'), "rank": user_data.get('rank', 'Initiate'),
            "e-mail": user_data['email'], "profile pic": user_data.get('profile_pic', None),
            "join date": join_date, "inventory": [], "credits": 0.0, "messages": [], "orders": []
        }
        st.session_state.users_db[user_data['email']] = new_user
        DatabaseManager.synchronize('users_db')
        self.ledger.record_event("ENTITY_REGISTERED", new_user, join_date)
        return new_user

    @staticmethod
    def check_permission(user_rank: str, perm_node: str) -> bool:
        matrix = st.session_state.permissions_db.get(user_rank, {})
        return matrix.get(perm_node, False)

# =====================================================================
# 7. UI PORTAL MANAGER (متحكم واجهة النظام العام والأقسام الشاملة)
# =====================================================================
class UIManager:
    def __init__(self):
        self.time_engine = LordstireTimeEngine()
        self.ledger = LordstireBlockchain()
        self.auth = AuthManager(self.time_engine, self.ledger)
        DatabaseManager.initialize()

    @staticmethod
    def render_attachment(file_data, file_meta, unique_key):
        if file_data:
            try:
                f_bytes = base64.b64decode(file_data)
                if "image" in file_meta.get('type', ''): 
                    st.image(f_bytes, width=300)
                else: 
                    st.download_button("📥 Download Attached Resource", f_bytes, file_name=file_meta['name'], key=f"dl_{unique_key}")
            except Exception:
                st.caption("⚠️ Could not render file asset attachment.")

    def render_public_portal(self):
        st.title("Seraleesen Arts | Cryptographic Gateway")
        tab_log, tab_reg = st.tabs(["🔒 Access Secure Node", "📝 Initialize Profile Schema"])
        
        with tab_log:
            email = st.text_input("Node Cryptographic E-mail", key="login_email_input")
            if st.button("Activate Link", key="login_btn"):
                if email in st.session_state.users_db:
                    st.session_state.current_user = st.session_state.users_db[email]
                    self.ledger.record_event("AUTH_LOGIN", {"email": email}, self.time_engine.get_timestamp())
                    st.rerun()
                else: 
                    st.error("Authentication rejected. Node hash undetected.")

        with tab_reg:
            with st.form("reg_form"):
                name = st.text_input("Entity Identity Name *")
                email_input = st.text_input("Network E-mail *")
                title = st.text_input("Operational Title")
                utype = st.selectbox("Structural Nature", ["Saien", "Biological", "Automated Component"])
                pic_file = st.file_uploader("Upload Profile Frame", type=['png', 'jpg', 'jpeg'])
                
                pic_base64 = None
                if pic_file: pic_base64 = base64.b64encode(pic_file.read()).decode('utf-8')
                
                if st.form_submit_button("Seal Signature"):
                    if name and email_input:
                        if email_input not in st.session_state.users_db:
                            assigned_rank = "Supreme Lord" if not st.session_state.users_db else "Initiate"
                            self.auth.register({
                                "name": name, "email": email_input, "title": title,
                                "type": utype, "profile_pic": pic_base64, "rank": assigned_rank
                            })
                            st.success(f"Profile Sealed as [{assigned_rank}]! Proceed to Access tab.")
                        else: st.warning("Node exists.")

    def render_posts_feed(self, scope="all", target_author_id=None):
        st.subheader("Publication Field Flow")
        user = st.session_state.current_user
        
        filtered_posts = []
        for p in st.session_state.posts_db:
            is_public = p.get("is_public", False)
            author_id = p.get("author_id")

            if scope == "public" and is_public:
                filtered_posts.append(p)
            elif scope == "private" and not is_public and author_id == user.get('Id'):
                filtered_posts.append(p)
            elif scope == "profile" and author_id == target_author_id:
                if is_public or author_id == user.get('Id'):
                    filtered_posts.append(p)
            elif scope == "all":
                if is_public or author_id == user.get('Id'):
                    filtered_posts.append(p)

        if not filtered_posts:
            st.info("No publication blocks found matching this context profile.")
            return

        legacy_detected = False
        for idx, p in enumerate(reversed(filtered_posts)):
            if "reacts" not in p or not isinstance(p["reacts"], dict):
                p["reacts"] = {"⚡ Power": 0, "🪐 Cosmos": 0, "⚒️ Construct": 0}
                legacy_detected = True
            if "reacted_users" not in p: p["reacted_users"] = {}; legacy_detected = True
            if "comments" not in p: p["comments"] = []; legacy_detected = True

            unique_key = f"feed_post_{p.get('post_id', idx)}_{idx}"
            
            with st.container(border=True):
                c_head1, c_head2 = st.columns([3, 1])
                with c_head1:
                    repost_tag = f" 🔄 (Reposted from {p.get('original_author')})" if p.get('is_repost') else ""
                    st.markdown(f"**👤 {p.get('author', 'Unknown')}** {repost_tag} {'🔒 *[Private Node]*' if not p.get('is_public') else '🌐 *[Public]*'}")
                with c_head2:
                    st.caption(f"⏱️ {p.get('ts', 'N/A')}")
                
                st.write(p.get('content', ''))
                self.render_attachment(p.get('file_data'), p.get('file_meta'), f"post_{unique_key}")
                
                st.write("")
                c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
                with c1:
                    if st.button(f"⚡ Power ({p['reacts'].get('⚡ Power', 0)})", key=f"r1_{unique_key}"):
                        SocialEngine.trigger_react(p['post_id'], user.get('Id'), "⚡ Power", self.time_engine.get_timestamp(), self.ledger)
                        st.rerun()
                with c2:
                    if st.button(f"🪐 Cosmos ({p['reacts'].get('🪐 Cosmos', 0)})", key=f"r2_{unique_key}"):
                        SocialEngine.trigger_react(p['post_id'], user.get('Id'), "🪐 Cosmos", self.time_engine.get_timestamp(), self.ledger)
                        st.rerun()
                with c3:
                    if st.button(f"⚒️ Construct ({p['reacts'].get('⚒️ Construct', 0)})", key=f"r3_{unique_key}"):
                        SocialEngine.trigger_react(p['post_id'], user.get('Id'), "⚒️ Construct", self.time_engine.get_timestamp(), self.ledger)
                        st.rerun()
                with c4:
                    if st.button("🔄 Repost to Matrix", key=f"rep_{unique_key}"):
                        SocialEngine.share_repost(p['post_id'], user.get('Id'), user.get('name'), self.time_engine.get_timestamp(), self.ledger)
                        st.success("Synchronized and Reposted!")
                        st.rerun()

                # FIX: Swapped "circle" to standard emoji symbol to prevent load exception
                st.markdown("**Comments Vector Matrix:**")
                for cm in p.get("comments", []):
                    with st.chat_message(name=cm.get('author', 'Entity'), avatar="💬"):
                        st.write(cm.get('text', ''))
                        self.render_attachment(cm.get('file_data'), cm.get('file_meta'), f"cm_{cm.get('comment_id')}")
                        st.caption(f"Sent at {cm.get('ts')}")
                
                with st.expander("💬 Append Comment Vector Block"):
                    with st.form(key=f"f_comm_{unique_key}", clear_on_submit=True):
                        in_comm = st.text_input("Comment Text Signature...", max_chars=300)
                        comm_file = st.file_uploader("Attach Resource File to Comment", type=None, key=f"file_cm_{unique_key}")
                        if st.form_submit_button("Commit Comment Stack"):
                            if in_comm or comm_file:
                                SocialEngine.add_comment(p['post_id'], user.get('name'), in_comm, comm_file, self.time_engine.get_timestamp(), self.ledger)
                                st.rerun()
        
        if legacy_detected:
            DatabaseManager.synchronize('posts_db')

    def render_private_workspace(self):
        user = st.session_state.current_user
        user_email = user.get('e-mail', user.get('email'))
        
        if user_email in st.session_state.users_db:
            user = st.session_state.users_db[user_email]
        user_rank = user.get('rank', 'Initiate')

        st.sidebar.title("Seraleesen Core")
        if user.get("profile pic"):
            st.sidebar.image(base64.b64decode(user["profile pic"]), width=100)
        
        st.sidebar.success(f"[{user.get('title', 'Entity')}] {user.get('name')}")
        st.sidebar.info(f"🛡️ Rank Node: {user_rank}")
        st.sidebar.caption(f"⏱️ {self.time_engine.get_timestamp()}")
        
        if st.sidebar.button("Disconnect Node", key="logout_system_btn"):
            self.ledger.record_event("AUTH_LOGOUT", {"email": user_email}, self.time_engine.get_timestamp())
            st.session_state.current_user = None
            st.rerun()
            
        st.sidebar.divider()
        
        menu = [
            "Dashboard & Comms", 
            "Public Vectors",
            "Registered Entities",
            "Administration (Global Editor)", 
            "Warehouse & Treasury", 
            "Accounting", 
            "Factory & Production", 
            "Store", 
            "R&D & Library", 
            "Campaigns & Camps", 
            "Blockchain Ledger"
        ]
        choice = st.sidebar.radio("Core Vector Nodes", menu)
        st.title(f"System Node Module | {choice}")
        st.divider()

        # --- ENGINE GLOBAL SEARCH ---
        st.sidebar.subheader("🔍 Global Search Deep Scan")
        search_query = st.sidebar.text_input("Search nodes, posts, or profiles...", key="global_search").strip().lower()
        if search_query:
            st.header(f"🔎 Deep Scan Results for: '{search_query}'")
            s_tab1, s_tab2 = st.tabs(["📄 Matching Publications", "👥 Registered Entities"])
            with s_tab1:
                for p in st.session_state.posts_db:
                    if search_query in p.get("content", "").lower() or search_query in p.get("author", "").lower():
                        st.info(f"From {p.get('author')} ({p.get('ts')}): {p.get('content', '')[:100]}...")
            with s_tab2:
                for u_k, u_v in st.session_state.users_db.items():
                    if search_query in u_v.get("name", "").lower() or search_query in u_k.lower() or search_query in u_v.get("title","").lower():
                        st.success(f"Entity: {u_v.get('name')} | E-mail: {u_k} | Rank: {u_v.get('rank')}")
            st.divider()

        # --- INTERFACE 1: DASHBOARD & COMMUNICATIONS ---
        if choice == "Dashboard & Comms":
            c1, c2 = st.columns([1.2, 1.8])
            with c1:
                st.subheader("Secure Direct Messages Node")
                recipients = [k for k in st.session_state.users_db.keys() if k != user_email]
                if recipients:
                    target_node_mail = st.selectbox("Select Target Node Schema:", recipients, key="dm_target_select")
                    target_user_obj = st.session_state.users_db[target_node_mail]
                    
                    with st.container(height=350, border=True):
                        for d in st.session_state.dms_db:
                            if (d.get('sender_id') == user.get('Id') and d.get('receiver_id') == target_user_obj.get('Id')) or \
                               (d.get('receiver_id') == user.get('Id') and d.get('sender_id') == target_user_obj.get('Id')):
                                # FIX: Removed "circle" option and replaced with valid Streamlit avatar keywords
                                with st.chat_message(name=d.get('sender_name'), avatar="user" if d.get('sender_id') == user.get('Id') else "assistant"):
                                    st.write(d.get('text'))
                                    self.render_attachment(d.get('file_data'), d.get('file_meta'), f"dm_{d.get('dm_id')}")
                                    st.caption(f"Timestamp: {d.get('ts')}")
                    
                    with st.form(key="dm_transmit_form", clear_on_submit=True):
                        dm_message = st.text_input("Type Direct Message Stack...")
                        dm_file = st.file_uploader("Attach Asset Frame", type=None)
                        if st.form_submit_button("Transmit Secured DM Package"):
                            if dm_message or dm_file:
                                SocialEngine.send_private_message(user.get('Id'), user.get('name'), target_user_obj['Id'], dm_message, dm_file, self.time_engine.get_timestamp(), self.ledger)
                                st.rerun()
                else:
                    st.info("No alternative node vectors mapped to network.")

                st.divider()
                st.subheader("Sub-Space Public Chat Stream")
                with st.container(height=350, border=True):
                    for m in st.session_state.chat_db:
                        # FIX: Swapped "circle" to standard emoji avatar
                        with st.chat_message(name=m.get('sender_name'), avatar="👤"):
                            st.write(m.get('text'))
                            st.caption(f"Sync Frame: {m.get('ts')}")
                            
                with st.form(key="public_chat_form", clear_on_submit=True):
                    chat_text = st.text_input("Broadcast text signal to matrix...")
                    if st.form_submit_button("Broadcast Singularity Packet"):
                        if chat_text:
                            msg = {"msg_id": str(uuid.uuid4()), "sender_id": user.get('Id'), "sender_name": user.get('name'), "text": chat_text, "ts": self.time_engine.get_timestamp()}
                            st.session_state.chat_db.append(msg)
                            DatabaseManager.synchronize('chat_db')
                            self.ledger.record_event("GLOBAL_CHAT_BROADCAST", {"sender": user.get('name')}, self.time_engine.get_timestamp())
                            st.rerun()

            with c2:
                st.subheader("Publish Internal Node Vector")
                with st.form("post_form", clear_on_submit=True):
                    post_text = st.text_area("Write publication specifications...")
                    uploaded_file = st.file_uploader("Attach Resource Object Frame", type=None)
                    is_pub_flag = st.checkbox("Publish Globally to Open Network (Public Vector)")
                    if st.form_submit_button("Deploy Node Block"):
                        if post_text or uploaded_file:
                            SocialEngine.add_post(user.get('Id'), user.get('name'), post_text, uploaded_file, is_pub_flag, self.time_engine.get_timestamp(), self.ledger)
                            st.rerun()
                
                st.divider()
                st.subheader("Your Personal & Isolated Feed Vectors")
                # Checked and matched call profile signature
                self.render_posts_feed(scope="private")

        # --- INTERFACE 2: PUBLIC VECTORS ---
        elif choice == "Public Vectors":
            st.info("Decentralized data stream open to all authenticated cluster endpoints.")
            self.render_posts_feed(scope="public")

        # --- INTERFACE 3: REGISTERED ENTITIES ---
        elif choice == "Registered Entities":
            st.subheader("Network Node Profile Registry Explorer")
            all_users = st.session_state.users_db
            
            if not all_users:
                st.warning("No records present inside cluster registry.")
            else:
                selected_entity_mail = st.selectbox("Select Target Node Address to Inspect:", list(all_users.keys()))
                if selected_entity_mail:
                    ent = all_users[selected_entity_mail]
                    with st.container(border=True):
                        cp1, cp2 = st.columns([1, 3])
                        with cp1:
                            if ent.get("profile pic"):
                                st.image(base64.b64decode(ent["profile pic"]), width=150)
                            else:
                                st.error("No Graphic Identity Frame Asset Saved.")
                        with cp2:
                            st.markdown(f"### Profile Entity: {ent.get('name')}")
                            st.write(f"**Operational Title:** {ent.get('title', 'N/A')}")
                            st.write(f"**Security Authorization Node Rank:** {ent.get('rank', 'Initiate')}")
                            st.write(f"**Structural Core Nature:** {ent.get('type', 'Saien')}")
                            st.write(f"**Chronological Matrix Connection Stamp:** {ent.get('join date', 'N/A')}")
                            st.write(f"**Internal Value Balance (Credits):** {ent.get('credits', 0.0)}")

                    st.divider()
                    st.subheader(f"Publications Vector Matrix for Entity: [{ent.get('name')}]")
                    self.render_posts_feed(scope="profile", target_author_id=ent.get("Id"))

        # --- INTERFACE 4: ADMINISTRATION ---
        elif choice == "Administration (Global Editor)":
            if not AuthManager.check_permission(user_rank, "edit_users"):
                st.error("Security Access Violation: Current configuration lacks data mutation privileges.")
                self.ledger.record_event("UNAUTHORIZED_ACCESS_ATTEMPT", {"user": user.get('name'), "rank": user_rank}, self.time_engine.get_timestamp())
            else:
                st.success("Cryptographic Cleared: Administrative Schema Access Active.")
                if AuthManager.check_permission(user_rank, "edit_perms"):
                    st.subheader("Core System Permissions Matrix Modification")
                    c_user_select = st.selectbox("Select Node Target Address:", list(st.session_state.users_db.keys()))
                    if c_user_select:
                        target_entity = st.session_state.users_db[c_user_select]
                        st.write(f"Current Rank Node for **{target_entity.get('name')}**: `{target_entity.get('rank', 'Initiate')}`")
                        new_assigned_rank = st.selectbox("Choose Overwrite Rank Profile Matrix:", ["Supreme Lord", "High Commander", "Initiate", "Contributor"])
                        if st.button("Enforce Database Rank Structural Overwrite"):
                            st.session_state.users_db[c_user_select]['rank'] = new_assigned_rank
                            DatabaseManager.synchronize('users_db')
                            self.ledger.record_event("USER_RANK_MUTATED", {"node": c_user_select, "rank": new_assigned_rank}, self.time_engine.get_timestamp())
                            st.success("Target State updated successfully.")
                            st.rerun()
                    
                    st.write("---")
                    edited_perms = st.data_editor(pd.DataFrame(st.session_state.permissions_db).T)
                    if st.button("Commit Node Permission Overrides"):
                        st.session_state.permissions_db = edited_perms.to_dict(orient='index')
                        DatabaseManager.synchronize('permissions_db')
                        st.success("Permissions system mutated on disk array.")
                        st.rerun()
                
                st.write("---")
                st.subheader("Raw Memory Table Direct Manipulation Matrix")
                db_target = st.selectbox("Select Database File Stack Target:", ["users_db", "inventory_db", "store_db", "campaigns_db"])
                target_data = st.session_state[db_target]
                if target_data:
                    df = pd.DataFrame.from_dict(target_data, orient='index')
                    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
                    if st.button("Write Buffer State Array Directly to Drive Drive"):
                        st.session_state[db_target] = edited_df.to_dict(orient='index')
                        DatabaseManager.synchronize(db_target)
                        st.success("Memory arrays serialized safely.")
                        st.rerun()

        # --- PLUGINS FOR REMAINING ORIGINAL SECTIONS ---
        elif choice == "Warehouse & Treasury": st.info("Asset Matrix, Raw Basalt Compounds & Mineral Reserves monitoring node active.")
        elif choice == "Accounting": st.info("Circular economics financial audits, resource valuation, and ledger auditing active.")
        elif choice == "Factory & Production": st.info("Industrial line control (Miniature Tractors & Bulldozers assembly processing) active.")
        elif choice == "Store": st.info("Trade interface for raw minerals, silica extraction assets, and art productions active.")
        elif choice == "R&D & Library": st.info("Vector Embeddings engine, Small Language Models sandbox, and Semitic Chronicle Archives waiting connection.")
        elif choice == "Campaigns & Camps": st.info("Field gathering expeditions, resource harvesting operations, and structural camp logs node active.")
        
        # --- INTERFACE 11: BLOCKCHAIN LEDGER ---
        elif choice == "Blockchain Ledger":
            if not AuthManager.check_permission(user_rank, "view_blockchain"):
                st.error("Cryptographic Exception: Read Access Blocked by Security Engine Policy Rule.")
            else:
                st.success("Immutable Blockchain Structural Chronicle Chain Stream Online.")
                for b in reversed(st.session_state.chain):
                    with st.expander(f"Block Sequence #{b.get('index')} | Action Node: {b.get('action')} | Time Matrix: {b.get('ts')}"):
                        st.write(f"**Hash Signature String:** `{b.get('hash')}`")
                        st.write(f"**Previous Linked Crypt Hash Anchor:** `{b.get('prev')}`")
                        st.json(b.get('details', {}))

    def run(self):
        if st.session_state.current_user is None:
            self.render_public_portal()
        else:
            self.render_private_workspace()

if __name__ == "__main__":
    app = UIManager()
    app.run()
