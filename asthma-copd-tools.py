import streamlit as st

# --- 🧠 ฟังก์ชันคำนวณ Predicted PEFR (อ้างอิงมาตรฐานประชากรไทย ปี 2000) ---
def calculate_predicted_pefr(age, height, sex):
    """
    สูตรคำนวณสกัดจากตาราง Reference spirometric values for healthy lifetime 
    nonsmokers in Thailand (Dejsomritrutai W, et al. 2000)
    """
    if sex == "ชาย":
        pefr = (18.425 * age) - (0.10815 * (age**2)) + (8.455 * height) - (0.05994 * age * height) - 1011.1
    else:
        pefr = (9.726 * age) - (0.05037 * (age**2)) + (23.622 * height) - (0.05987 * (height**2)) - (0.04323 * age * height) - 1895.5
    
    return max(0, round(pefr)) # ปัดเศษให้เป็นจำนวนเต็ม และไม่ให้ติดลบ

# --- ⚙️ การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Asthma/COPD Follow-up Dashboard", layout="wide")
st.title("🫁 Asthma/COPD Follow-up Dashboard")
st.markdown("ระบบบันทึกและประเมินผลการรักษาผู้ป่วยโรคทางเดินหายใจตีบ 🏥✨")

# สร้าง Tabs สำหรับแบ่งหน้าจอการทำงาน
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "👤 1. ข้อมูลทั่วไป", 
    "🗣️ 2. ประเมินอาการ", 
    "🫁 3. สมรรถภาพปอด", 
    "💊 4. การใช้ยา", 
    "📊 5. CAT Score (COPD)", 
    "👨‍⚕️ สรุปสำหรับแพทย์"
])

# --- ตัวแปรสำหรับเก็บคะแนน ---
if 'cat_score' not in st.session_state: st.session_state.cat_score = 0
if 'asthma_control_score' not in st.session_state: st.session_state.asthma_control_score = 0

# ==========================================
# 👤 ส่วนที่ 1: ข้อมูลทั่วไปและสัญญาณชีพ
# ==========================================
with tab1:
    st.header("👤 ส่วนที่ 1: ข้อมูลทั่วไปและสัญญาณชีพ")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        disease_type = st.radio("ประเภทโรค 📌", ["Asthma (โรคหืด)", "COPD (ปอดอุดกั้นเรื้อรัง)", "Asthma-COPD Overlap"])
        age = st.number_input("อายุ (ปี) 🎂", min_value=15, max_value=120, value=60)
        sex = st.radio("เพศ 🚻", ["ชาย", "หญิง"])
        
    with col2:
        weight = st.number_input("น้ำหนัก (กก.) ⚖️", value=60.0)
        height = st.number_input("ส่วนสูง (ซม.) 📏", value=160.0)
        
        # คำนวณ BMI
        bmi = weight / ((height/100)**2) if height > 0 else 0
        st.info(f"💡 BMI: {bmi:.1f}")
        
    with col3:
        # 🌟 Smart Feature: คำนวณ Predicted PEFR ตามมาตรฐานคนไทย!
        pred_pefr = calculate_predicted_pefr(age, height, sex)
        st.success(f"🎯 ค่า Predicted PEFR อัตโนมัติ: **{pred_pefr} L/min**")
        st.caption("อ้างอิง: สมาคมอุรเวชช์แห่งประเทศไทย (Dejsomritrutai W, et al. 2000)")

# ==========================================
# 🗣️ ส่วนที่ 2: การประเมินอาการ 4 สัปดาห์
# ==========================================
with tab2:
    st.header("🗣️ ส่วนที่ 2: การประเมินอาการ (4 สัปดาห์ที่ผ่านมา)")
    
    st.subheader("1. การควบคุมอาการ (Symptom Control)")
    day_symp = st.selectbox("☀️ อาการหอบ/ไอ กลางวัน", ["0 - ไม่มี", "1 - < 1 ครั้ง/สัปดาห์", "2 - >= 1 ครั้ง/สัปดาห์", "3 - ทุกวัน", "4 - เกือบตลอดเวลา"])
    night_symp = st.selectbox("🌙 อาการหอบ/ไอ กลางคืน (จนต้องตื่น)", ["0 - ไม่มี", "1 - <= 2 ครั้ง/เดือน", "2 - > 2 ครั้ง/เดือน", "3 - > 1 ครั้ง/สัปดาห์", "4 - เกือบทุกวัน"])
    rescue_med = st.selectbox("💊 การใช้ยาบรรเทาอาการฉุกเฉิน", ["0 - ไม่มี", "1 - < 1 ครั้ง/สัปดาห์", "2 - เกือบทุกวัน", "3 - ทุกวัน", "4 - > 4 ครั้ง/วัน ติดต่อกัน >=2 วัน"])
    
    st.subheader("2. ประวัติกำเริบ (Exacerbation)")
    col_ex1, col_ex2 = st.columns(2)
    with col_ex1:
        er_visit = st.number_input("🚑 จำนวนครั้งที่ต้องไป ER / คลินิกฉุกเฉิน (ครั้ง)", min_value=0, value=0)
    with col_ex2:
        admit_days = st.number_input("🏥 จำนวนวันที่ต้อง Admit นอนโรงพยาบาล (วัน)", min_value=0, value=0)
        
    st.subheader("3. อาการปัจจุบัน")
    col_cur1, col_cur2, col_cur3 = st.columns(3)
    with col_cur1:
        smoking = st.checkbox("🚬 ปัจจุบันยังสูบบุหรี่")
    with col_cur2:
        sputum = st.checkbox("🤧 มีเสมหะเหลือง/เขียว")
    with col_cur3:
        mmrc = st.selectbox("เหนื่อยหอบ (mMRC)", ["0 - เหนื่อยเมื่อออกกำลังหนัก", "1 - เหนื่อยเมื่อรีบเดิน/ขึ้นเนิน", "2 - เดินช้ากว่าคนวัยเดียวกัน", "3 - เดิน 100 เมตรต้องหยุดพัก", "4 - เหนื่อยมากจนออกจากบ้านไม่ได้"])

# ==========================================
# 🫁 ส่วนที่ 3: สมรรถภาพปอดและการทดสอบร่างกาย
# ==========================================
with tab3:
    st.header("🫁 ส่วนที่ 3: สมรรถภาพปอด (Lung Function & 6MWT)")
    
    col_lung1, col_lung2 = st.columns(2)
    with col_lung1:
        st.subheader("💨 Peak Flow (PEFR)")
        pre_pefr = st.number_input("Pre-PEFR ที่เป่าได้ (L/min)", min_value=0, value=0)
        post_pefr = st.number_input("Post-PEFR ที่เป่าได้ (L/min) [หลังพ่นยา]", min_value=0, value=0)
        
        # 🌟 Smart Feature: คำนวณ % Predicted
        if pred_pefr > 0 and pre_pefr > 0:
            pct_pred = (pre_pefr / pred_pefr) * 100
            if pct_pred >= 80:
                st.success(f"🟢 % Predicted: {pct_pred:.1f}% (โซนสีเขียว)")
            elif pct_pred >= 50:
                st.warning(f"🟡 % Predicted: {pct_pred:.1f}% (โซนสีเหลือง - ควรเฝ้าระวัง)")
            else:
                st.error(f"🔴 % Predicted: {pct_pred:.1f}% (โซนสีแดง - อันตราย/วิกฤต)")
                
    with col_lung2:
        st.subheader("🚶‍♂️ 6 Minute Walk Test & Vitals")
        walk_dist = st.number_input("ระยะทางเดิน 6 นาที (เมตร)", min_value=0, value=0)
        o2_sat = st.number_input("O2 Saturation (%)", min_value=0, max_value=100, value=98)
        
        if o2_sat < 90 and o2_sat > 0:
            st.error("🚨 ระวัง! O2 Saturation ต่ำกว่า 90%")

# ==========================================
# 💊 ส่วนที่ 4: การใช้ยา ผลข้างเคียง และความร่วมมือ
# ==========================================
with tab4:
    st.header("💊 ส่วนที่ 4: การใช้ยาและความร่วมมือ (Adherence)")
    
    st.subheader("⚠️ ผลข้างเคียงจากการใช้ยา")
    side_effects = st.multiselect("เลือกผลข้างเคียงที่พบ:", ["ไม่มี", "เชื้อราในปาก 🍄", "เสียงแหบ 🗣️", "ใจสั่น 💓"])
    if "เชื้อราในปาก 🍄" in side_effects or "เสียงแหบ 🗣️" in side_effects:
        st.warning("💡 แนะนำ: กรุณาสอนผู้ป่วยบ้วนปากและกลั้วคอด้วยน้ำสะอาดหลังพ่นยาที่มีสเตียรอยด์ทุกครั้ง")
        
    st.subheader("✅ ความร่วมมือในการใช้ยา (Adherence)")
    adherence = st.slider("เภสัชกรประเมินการใช้ยา (%)", 0, 100, 100)
    if adherence < 80:
        st.error("🚨 ผู้ป่วยใช้ยาไม่สม่ำเสมอ (<80%) อาจเป็นสาเหตุหลักที่ทำให้ควบคุมอาการไม่ได้!")
        
    st.subheader("🎓 Checklist การให้ความรู้ (Education)")
    edu1 = st.checkbox("สอนความรู้เกี่ยวกับโรคแล้ว")
    edu2 = st.checkbox("สอนเทคนิคการพ่นยาแล้ว")
    edu3 = st.checkbox("ตรวจสอบแล้วว่าผู้ป่วยพ่นยาได้ **ถูกต้อง**")
    edu4 = st.checkbox("สอนเรื่องโทษและแนะนำการเลิกบุหรี่ (กรณีสูบ)")

# ==========================================
# 📊 ส่วนที่ 5: แบบประเมินเฉพาะ COPD (CAT Score)
# ==========================================
with tab5:
    st.header("📊 ส่วนที่ 5: แบบประเมิน CAT Score (สำหรับ COPD)")
    
    if "COPD" not in disease_type:
        st.info("ℹ️ ผู้ป่วยรายนี้เป็น Asthma ไม่จำเป็นต้องประเมิน CAT Score (สามารถข้ามแท็บนี้ได้)")
    else:
        st.write("ให้คะแนน 0-5 ในแต่ละหัวข้อ (0 = ไม่มีอาการ, 5 = เป็นมากที่สุด)")
        cat1 = st.slider("1. ไอ", 0, 5, 0)
        cat2 = st.slider("2. เสมหะ", 0, 5, 0)
        cat3 = st.slider("3. แน่นหน้าอก", 0, 5, 0)
        cat4 = st.slider("4. เหนื่อยหอบเมื่อเดินขึ้นเนิน/บันได", 0, 5, 0)
        cat5 = st.slider("5. ข้อจำกัดในการทำกิจกรรมที่บ้าน", 0, 5, 0)
        cat6 = st.slider("6. ความกังวลในการออกจากบ้าน", 0, 5, 0)
        cat7 = st.slider("7. การนอนหลับ", 0, 5, 0)
        cat8 = st.slider("8. พลังงาน/ความรู้สึกอ่อนเพลีย", 0, 5, 0)
        
        total_cat = cat1 + cat2 + cat3 + cat4 + cat5 + cat6 + cat7 + cat8
        st.session_state.cat_score = total_cat
        
        st.write("---")
        if total_cat < 10:
            st.success(f"🟢 CAT Score = {total_cat} (ผลกระทบต่อชีวิตประจำวัน **น้อย**)")
        else:
            st.error(f"🔴 CAT Score = {total_cat} (ผลกระทบต่อชีวิตประจำวัน **มาก** / ควรปรับแนวทางการรักษา)")

# ==========================================
# 👨‍⚕️ สรุปสำหรับแพทย์ (Doctor's Summary)
# ==========================================
with tab6:
    st.header("👨‍⚕️ สรุปผลการประเมินสำหรับแพทย์ (AI Summary)")
    st.markdown("---")
    
    # 🧠 Logic ประเมิน Level of Control (แบบง่าย)
    symptom_count = 0
    if not day_symp.startswith("0"): symptom_count += 1
    if not night_symp.startswith("0"): symptom_count += 1
    if not rescue_med.startswith("0"): symptom_count += 1
    
    st.subheader("1. ระดับการควบคุมโรค (Level of Control)")
    if symptom_count == 0:
        st.success("🟢 **Well Controlled (ควบคุมได้ดี)** - ไม่มีอาการรบกวน")
    elif symptom_count <= 2:
        st.warning("🟡 **Partially Controlled (ควบคุมได้บางส่วน)** - มีอาการรบกวนบ้าง")
    else:
        st.error("🔴 **Uncontrolled (ควบคุมไม่ได้)** - มีอาการรบกวนบ่อยครั้ง")
        
    st.subheader("2. ประวัติกำเริบ (Risk of Exacerbation)")
    if er_visit > 0 or admit_days > 0:
        st.error(f"🚨 **High Risk!** มีประวัติกำเริบใน 4 สัปดาห์ (เข้า ER {er_visit} ครั้ง, Admit {admit_days} วัน)")
    else:
        st.success("✅ ไม่มีประวัติกำเริบรุนแรงใน 4 สัปดาห์ที่ผ่านมา")
        
    st.subheader("3. การทำงานของปอด (Lung Function)")
    if pre_pefr > 0:
        pct = (pre_pefr / pred_pefr) * 100
        st.info(f"💨 PEFR: {pre_pefr} L/min คิดเป็น **{pct:.1f}% Predicted**")
    else:
        st.write("ไม่มีข้อมูลการเป่าปอดในครั้งนี้")
        
    st.subheader("4. 💡 คำแนะนำทางคลินิก (Clinical Suggestion)")
    suggestions = []
    if adherence < 80:
        suggestions.append("⚠️ ผู้ป่วยใช้ยาไม่สม่ำเสมอ แนะนำค้นหาสาเหตุและแก้ไขเทคนิคการพ่นยาก่อนพิจารณาปรับเพิ่ม Step ยา")
    if not edu3:
        suggestions.append("⚠️ ยังไม่ได้ตรวจสอบเทคนิคการพ่นยา (Inhaler Technique) ว่าถูกต้องหรือไม่")
    if smoking:
        suggestions.append("🚬 ผู้ป่วยยังสูบบุหรี่ ควรเน้นย้ำ Smoking Cessation")
    if "COPD" in disease_type and st.session_state.cat_score >= 10:
        suggestions.append(f"🔴 CAT Score สูง ({st.session_state.cat_score}) แนะนำพิจารณาปรับยาขยายหลอดลม (LAMA/LABA) หรือทำ Pulmonary Rehab")
    if er_visit > 0 or admit_days > 0:
        suggestions.append("🚨 มีประวัติ Exacerbation ควรพิจารณาปรับ Step ยาขึ้น (Step-up Therapy) หรือพิจารณาให้ ICS/Oral Steroid ตามความเหมาะสม")
        
    if len(suggestions) > 0:
        for s in suggestions:
            st.write(f"- {s}")
    else:
        st.write("✨ แนะนำให้การรักษาเดิม (Maintain current therapy) และติดตามอาการตามนัด")
