import streamlit as st
from fpdf import FPDF
import tempfile
import os

# --- ⚙️ การตั้งค่าหน้าจอ (ต้องอยู่บรรทัดแรกเสมอ) ---
st.set_page_config(page_title="Asthma/COPD Follow-up Dashboard", layout="wide")

# --- 🧠 ฟังก์ชันคำนวณ Predicted PEFR (อ้างอิงมาตรฐานประชากรไทย ปี 2000) ---
def calculate_predicted_pefr(age, height, sex):
    if sex == "ชาย":
        pefr = (18.425 * age) - (0.10815 * (age**2)) + (8.455 * height) - (0.05994 * age * height) - 1011.1
    else:
        pefr = (9.726 * age) - (0.05037 * (age**2)) + (23.622 * height) - (0.05987 * (height**2)) - (0.04323 * age * height) - 1895.5
    return max(0, round(pefr))

# --- 📄 ฟังก์ชันสร้างไฟล์ PDF ขนาด A4 ---
def generate_pdf_report(data):
    pdf = FPDF(format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # ตรวจสอบและโหลดฟอนต์ภาษาไทย
    font_path = "THSarabunNew.ttf"
    has_thai_font = os.path.exists(font_path)
    
    if has_thai_font:
        pdf.add_font("THSarabunNew", fname=font_path)
        pdf.set_font("THSarabunNew", size=24)
    else:
        pdf.set_font("Arial", size=16)
        
    # 1. หัวกระดาษ (Header)
    if has_thai_font:
        pdf.cell(0, 10, "รายงานสรุปการประเมิน Asthma / COPD", align="C", ln=True)
        pdf.set_font("THSarabunNew", size=16)
    else:
        pdf.cell(0, 10, "Asthma / COPD Assessment Report", align="C", ln=True)
        pdf.set_font("Arial", size=12)
        
    pdf.line(10, 25, 200, 25)
    pdf.ln(10)
    
    # ฟังก์ชันช่วยเขียนข้อมูลเป็นบรรทัด
    def add_row(label, value):
        pdf.cell(70, 8, txt=label, ln=0)
        pdf.cell(0, 8, txt=str(value), ln=True)
        
    # 2. ข้อมูลผู้ป่วย
    add_row("ประเภทโรค (Disease):", data['disease'])
    add_row("อายุ (Age):", f"{data['age']} ปี")
    add_row("เพศ (Sex):", data['sex'])
    add_row("ดัชนีมวลกาย (BMI):", f"{data['bmi']:.1f}")
    add_row("ค่าเป้าหมายปอด (Predicted PEFR):", f"{data['pred_pefr']} L/min")
    
    pdf.ln(5)
    
    # 3. ผลการประเมิน
    if has_thai_font: pdf.set_font("THSarabunNew", size=18)
    pdf.cell(0, 8, "ผลการประเมินทางคลินิก (Clinical Assessment):", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    
    if has_thai_font: pdf.set_font("THSarabunNew", size=16)
    add_row("ระดับการควบคุมโรค (Control Level):", data['control'])
    add_row("ความเสี่ยงกำเริบ (Exacerbation Risk):", data['risk'])
    add_row("สมรรถภาพปอด (%Predicted PEFR):", f"{data['pct_pred']:.1f}%")
    add_row("ความร่วมมือในการใช้ยา (Adherence):", f"{data['adherence']}%")
    
    if "COPD" in data['disease']:
        add_row("คะแนน CAT Score:", f"{data['cat']} คะแนน")
        
    pdf.ln(5)
    
    # 4. คำแนะนำสำหรับแพทย์
    if has_thai_font: pdf.set_font("THSarabunNew", size=18)
    pdf.cell(0, 8, "สรุปและคำแนะนำ (Doctor's Summary & Suggestions):", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    
    if has_thai_font: pdf.set_font("THSarabunNew", size=16)
    for sug in data['suggestions']:
        # ใช้ multi_cell เพื่อให้ข้อความยาวๆ ขึ้นบรรทัดใหม่ได้อัตโนมัติ
        pdf.multi_cell(0, 8, txt=f"- {sug}")
        
    pdf.ln(20)
    pdf.cell(0, 8, "ลงชื่อผู้ประเมิน.......................................................", align="R", ln=True)
    pdf.cell(0, 8, "วันที่........./........./.........", align="R", ln=True)
    
    # สร้างไฟล์ชั่วคราว
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(tmp_file.name)
    return tmp_file.name

# ==========================================
# UI หน้าเว็บหลัก
# ==========================================
st.title("🫁 Asthma/COPD Follow-up Dashboard")
st.markdown("ระบบบันทึกและประเมินผลการรักษาผู้ป่วยโรคทางเดินหายใจตีบ 🏥✨")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "👤 1. ข้อมูลทั่วไป", "🗣️ 2. ประเมินอาการ", "🫁 3. สมรรถภาพปอด", 
    "💊 4. การใช้ยา", "📊 5. CAT Score (COPD)", "👨‍⚕️ สรุปสำหรับแพทย์"
])

if 'cat_score' not in st.session_state: st.session_state.cat_score = 0

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
        bmi = weight / ((height/100)**2) if height > 0 else 0
        st.info(f"💡 BMI: {bmi:.1f}")
    with col3:
        pred_pefr = calculate_predicted_pefr(age, height, sex)
        st.success(f"🎯 Predicted PEFR: **{pred_pefr} L/min**")
        st.caption("อ้างอิง: สมาคมอุรเวชช์แห่งประเทศไทย (2000)")

with tab2:
    st.header("🗣️ ส่วนที่ 2: การประเมินอาการ (4 สัปดาห์ที่ผ่านมา)")
    day_symp = st.selectbox("☀️ อาการหอบ/ไอ กลางวัน", ["0 - ไม่มี", "1 - < 1 ครั้ง/สัปดาห์", "2 - >= 1 ครั้ง/สัปดาห์", "3 - ทุกวัน", "4 - เกือบตลอดเวลา"])
    night_symp = st.selectbox("🌙 อาการหอบ/ไอ กลางคืน", ["0 - ไม่มี", "1 - <= 2 ครั้ง/เดือน", "2 - > 2 ครั้ง/เดือน", "3 - > 1 ครั้ง/สัปดาห์", "4 - เกือบทุกวัน"])
    rescue_med = st.selectbox("💊 การใช้ยาบรรเทาอาการฉุกเฉิน", ["0 - ไม่มี", "1 - < 1 ครั้ง/สัปดาห์", "2 - เกือบทุกวัน", "3 - ทุกวัน", "4 - > 4 ครั้ง/วัน ติดต่อกัน >=2 วัน"])
    col_ex1, col_ex2 = st.columns(2)
    with col_ex1: er_visit = st.number_input("🚑 ครั้งที่ไป ER (ครั้ง)", min_value=0, value=0)
    with col_ex2: admit_days = st.number_input("🏥 วันที่ Admit (วัน)", min_value=0, value=0)
    col_cur1, col_cur2, col_cur3 = st.columns(3)
    with col_cur1: smoking = st.checkbox("🚬 ปัจจุบันยังสูบบุหรี่")
    with col_cur2: sputum = st.checkbox("🤧 มีเสมหะเหลือง/เขียว")
    with col_cur3: mmrc = st.selectbox("เหนื่อยหอบ (mMRC)", ["0", "1", "2", "3", "4"])

with tab3:
    st.header("🫁 ส่วนที่ 3: สมรรถภาพปอด (Lung Function & 6MWT)")
    col_lung1, col_lung2 = st.columns(2)
    with col_lung1:
        pre_pefr = st.number_input("Pre-PEFR ที่เป่าได้ (L/min)", min_value=0, value=0)
        post_pefr = st.number_input("Post-PEFR ที่เป่าได้ (L/min)", min_value=0, value=0)
        if pred_pefr > 0 and pre_pefr > 0:
            pct_pred = (pre_pefr / pred_pefr) * 100
            if pct_pred >= 80: st.success(f"🟢 % Predicted: {pct_pred:.1f}% (เกณฑ์ดี)")
            elif pct_pred >= 50: st.warning(f"🟡 % Predicted: {pct_pred:.1f}% (เฝ้าระวัง)")
            else: st.error(f"🔴 % Predicted: {pct_pred:.1f}% (อันตราย)")
    with col_lung2:
        walk_dist = st.number_input("ระยะเดิน 6 นาที (เมตร)", min_value=0, value=0)
        o2_sat = st.number_input("O2 Saturation (%)", min_value=0, max_value=100, value=98)
        if o2_sat < 90 and o2_sat > 0: st.error("🚨 ระวัง! O2 Sat Drop")

with tab4:
    st.header("💊 ส่วนที่ 4: การใช้ยาและความร่วมมือ")
    side_effects = st.multiselect("ผลข้างเคียง:", ["ไม่มี", "เชื้อราในปาก", "เสียงแหบ", "ใจสั่น"])
    adherence = st.slider("การใช้ยา (%)", 0, 100, 100)
    edu1 = st.checkbox("สอนความรู้โรค")
    edu2 = st.checkbox("สอนพ่นยา")
    edu3 = st.checkbox("เช็คว่าพ่นยาถูกต้อง")
    edu4 = st.checkbox("แนะนำเลิกบุหรี่")

with tab5:
    st.header("📊 ส่วนที่ 5: CAT Score (สำหรับ COPD)")
    if "COPD" not in disease_type:
        st.info("ℹ️ ผู้ป่วย Asthma ข้ามแท็บนี้ได้เลยครับ")
    else:
        cat1 = st.slider("1. ไอ", 0, 5, 0)
        cat2 = st.slider("2. เสมหะ", 0, 5, 0)
        cat3 = st.slider("3. แน่นหน้าอก", 0, 5, 0)
        cat4 = st.slider("4. เหนื่อยขึ้นบันได", 0, 5, 0)
        cat5 = st.slider("5. ข้อจำกัดกิจกรรม", 0, 5, 0)
        cat6 = st.slider("6. กังวลออกจากบ้าน", 0, 5, 0)
        cat7 = st.slider("7. การนอน", 0, 5, 0)
        cat8 = st.slider("8. อ่อนเพลีย", 0, 5, 0)
        st.session_state.cat_score = cat1 + cat2 + cat3 + cat4 + cat5 + cat6 + cat7 + cat8
        st.write(f"**รวมคะแนน: {st.session_state.cat_score}**")

with tab6:
    st.header("👨‍⚕️ สรุปผลการประเมินสำหรับแพทย์")
    
    # ประมวลผลข้อมูล
    symptom_count = sum(1 for symp in [day_symp, night_symp, rescue_med] if not symp.startswith("0"))
    control_level = "Well Controlled (ควบคุมได้ดี)" if symptom_count == 0 else ("Partially Controlled (ควบคุมได้บางส่วน)" if symptom_count <= 2 else "Uncontrolled (ควบคุมไม่ได้)")
    risk_level = "High Risk (มีประวัติกำเริบ)" if (er_visit > 0 or admit_days > 0) else "Low Risk (ไม่มีประวัติกำเริบใน 4 สัปดาห์)"
    pct = (pre_pefr / pred_pefr * 100) if pred_pefr > 0 and pre_pefr > 0 else 0
    
    # สร้างข้อความคำแนะนำ
    suggestions = []
    if adherence < 80: suggestions.append("ผู้ป่วยใช้ยาไม่สม่ำเสมอ แนะนำตรวจสอบสาเหตุและแก้ไขเทคนิคพ่นยา")
    if not edu3: suggestions.append("ยังไม่ได้ตรวจสอบเทคนิคพ่นยา ว่าถูกต้องหรือไม่")
    if smoking: suggestions.append("ผู้ป่วยยังสูบบุหรี่ ควรเน้นย้ำ Smoking Cessation")
    if "COPD" in disease_type and st.session_state.cat_score >= 10:
        suggestions.append(f"CAT Score สูง ({st.session_state.cat_score}) พิจารณาปรับยา หรือทำ Pulmonary Rehab")
    if er_visit > 0 or admit_days > 0:
        suggestions.append("มีประวัติ Exacerbation พิจารณา Step-up Therapy หรือ ICS/Oral Steroid")
    if not suggestions: suggestions.append("แนะนำให้การรักษาเดิม (Maintain current therapy) และติดตามอาการตามนัด")
    
    # แสดงผลบนหน้าจอ
    st.subheader(f"1. ระดับการควบคุม: {control_level}")
    st.subheader(f"2. ประวัติกำเริบ: {risk_level}")
    st.subheader("3. คำแนะนำ (Clinical Suggestions):")
    for s in suggestions: st.write(f"- {s}")
        
    st.markdown("---")
    st.subheader("📄 ส่งออกรายงาน (Export Report)")
    
    # เตรียมข้อมูลส่งเข้าฟังก์ชัน PDF
    report_data = {
        "disease": disease_type, "age": age, "sex": sex, "bmi": bmi,
        "pred_pefr": pred_pefr, "control": control_level, "risk": risk_level,
        "pct_pred": pct, "adherence": adherence, "cat": st.session_state.cat_score,
        "suggestions": suggestions
    }
    
    # ปุ่มกดสร้าง PDF
    if st.button("🖨️ สร้างและดาวน์โหลดไฟล์ PDF (A4)", type="primary"):
        with st.spinner("กำลังจัดหน้ากระดาษและสร้าง PDF... ⏳"):
            try:
                if not os.path.exists("THSarabunNew.ttf"):
                    st.warning("⚠️ ไม่พบไฟล์ฟอนต์ 'THSarabunNew.ttf' ระบบจะใช้ฟอนต์ภาษาอังกฤษแทน ซึ่งอาจทำให้ภาษาไทยอ่านไม่ออก")
                    
                pdf_path = generate_pdf_report(report_data)
                
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="📥 คลิกที่นี่เพื่อดาวน์โหลด PDF",
                        data=pdf_file,
                        file_name=f"Report_Asthma_COPD.pdf",
                        mime="application/pdf"
                    )
                st.success("✅ สร้างไฟล์ PDF สำเร็จแล้ว!")
            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาด: {e}")
