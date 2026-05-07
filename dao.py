import hashlib
import time

class Proposal:
    """ يمثل مقترحاً داخل الـ DAO (كتلة في السلسلة) """
    def __init__(self, index, prevHash, timestamp, data, proposer):
        self.index = index
        self.prevHash = prevHash
        self.timestamp = timestamp
        self.data = data # وصف المقترح
        self.proposer = proposer # الشخص الذي قدم المقترح
        self.votes_yes = 0 # عدد الأصوات المؤيدة
        self.votes_no = 0  # عدد الأصوات المعارضة
        self.hash = self.calc_hash()

    def calc_hash(self):
        """ حساب البصمة الرقمية للمقترح لضمان عدم التلاعب """
        payload = f"{self.index}{self.prevHash}{self.timestamp}{self.data}{self.proposer}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def vote(self, choice):
        """ إضافة صوت للمقترح (نعم أو لا) """
        if choice.lower() == "yes":
            self.votes_yes += 1
        elif choice.lower() == "no":
            self.votes_no += 1

class SlsDao:
    """ النظام الأساسي للـ DAO وإدارة البيانات """
    def __init__(self):
        # إنشاء أول كتلة في السلسلة (Genesis Block)
        genesis = Proposal(0, "0", int(time.time()), "DAO Activation", "System")
        self.chain = [genesis]
        self.members = ["Ali", "Sara", "Omar"] # قائمة الأعضاء المصرح لهم

    def add_proposal(self, member_name, proposal_text):
        """ إضافة مقترح جديد للسلسلة بعد التأكد من هوية العضو """
        if member_name not in self.members:
            print(f"❌ خطأ: {member_name} ليس عضواً في الـ DAO!")
            return False
        
        prev_block = self.chain[-1]
        new_proposal = Proposal(
            index=len(self.chain),
            prevHash=prev_block.hash,
            timestamp=int(time.time()),
            data=proposal_text,
            proposer=member_name
        )
        self.chain.append(new_proposal)
        print(f"✅ تم إضافة مقترح جديد من: {member_name}")
        return True

    def cast_vote(self, proposal_index, choice):
        """ التصويت على مقترح موجود مسبقاً """
        if 0 <= proposal_index < len(self.chain):
            self.chain[proposal_index].vote(choice)
            print(f"🗳️ تم تسجيل صوت بـ ({choice}) للمقترح رقم {proposal_index}")
        else:
            print("❌ رقم المقترح غير موجود!")

    def check_integrity(self):
        """ التحقق من صحة البيانات وعدم تعديلها تاريخياً """
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i-1]

            # التأكد أن البيانات لم تتغير (Hash check)
            if current.hash != current.calc_hash():
                print(f"⚠️ تحذير: تم التلاعب في بيانات المقترح رقم {i}")
                return False
            
            # التأكد أن السلسلة متصلة بشكل صحيح
            if current.prevHash != prev.hash:
                print(f"⚠️ تحذير: انقطاع في تسلسل البيانات عند المقترح {i}")
                return False
        return True

    def display_dao_status(self):
        """ عرض حالة المقترحات ونتائج التصويت """
        print("\n--- 📋 سجل مقترحات الـ DAO ---")
        for p in self.chain:
            status = "Approved" if p.votes_yes > p.votes_no else "Pending/Rejected"
            print(f"المقترح [{p.index}] | صاحب الطلب: {p.proposer}")
            print(f"التفاصيل: {p.data}")
            print(f"الأصوات: (نعم: {p.votes_yes} | لا: {p.votes_no}) | الحالة: {status}")
            print("-" * 40)

# --- تجربة النظام ---
if __name__ == "__main__":
    my_dao = SlsDao()

    # 1. إضافة مقترحات
    my_dao.add_proposal("Ali", "زيادة ميزانية التطوير 15%")
    my_dao.add_proposal("Sara", "توظيف مطور Python جديد")

    # 2. عملية التصويت
    my_dao.cast_vote(1, "yes")
    my_dao.cast_vote(1, "yes")
    my_dao.cast_vote(1, "no")
    my_dao.cast_vote(2, "yes")

    # 3. عرض النتائج والتحقق من الأمان
    my_dao.display_dao_status()
    print(f"هل البيانات آمنة وسليمة؟ {my_dao.check_integrity()}")
