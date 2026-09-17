import streamlit as st
from fpdf import FPDF
import tempfile
import os

# --- ⚙️ การตั้งค่าหน้าจอ ---
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
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
    import tempfile
    import os

    # ==========================================
    # 1. สร้าง PDF A4
    # ==========================================
    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4"
    )

    pdf.set_margins(
        left=10,
        top=12,
        right=10
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=18
    )

    pdf.add_page()

    # ==========================================
    # 2. โหลดฟอนต์ภาษาไทย
    # ==========================================
    font_path = "THSarabunNew.ttf"
    has_thai_font = os.path.exists(font_path)

    if has_thai_font:
        pdf.add_font(
            "THSarabunNew",
            fname=font_path
        )
        font_name = "THSarabunNew"
    else:
        font_name = "Arial"

    # ==========================================
    # 3. Helper: ตั้ง font
    # ==========================================
    def set_font(size=16):
        pdf.set_font(
            font_name,
            size=size
        )

    # ==========================================
    # 4. ขนาดพื้นที่
    # ==========================================
    PAGE_WIDTH = pdf.w - pdf.l_margin - pdf.r_margin

    LABEL_WIDTH = 65
    VALUE_WIDTH = PAGE_WIDTH - LABEL_WIDTH

    # ==========================================
    # 5. Helper: section title
    # ==========================================
    def add_section_title(title):

        set_font(17)

        pdf.multi_cell(
            w=PAGE_WIDTH,
            h=6,
            text=str(title),
            border=0,
            align="L",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            wrapmode="CHAR"
        )

        y = pdf.get_y()

        pdf.line(
            pdf.l_margin,
            y,
            pdf.w - pdf.r_margin,
            y
        )

        pdf.ln(1.5)

    # ==========================================
    # 6. Helper: ข้อมูล 1 row
    # ==========================================
    def add_secure_row(label, value):

        label = str(label)
        value = str(value) if value is not None else "-"

        set_font(15)

        # --------------------------------------
        # จำตำแหน่งเริ่มต้น
        # --------------------------------------
        start_x = pdf.get_x()
        start_y = pdf.get_y()

        # --------------------------------------
        # วัดความสูงของ Label
        # --------------------------------------
        label_height = pdf.multi_cell(
            w=LABEL_WIDTH,
            h=6,
            text=label,
            border=0,
            dry_run=True,
            output="HEIGHT",
            wrapmode="CHAR"
        )

        # --------------------------------------
        # วัดความสูงของ Value
        # --------------------------------------
        value_height = pdf.multi_cell(
            w=VALUE_WIDTH,
            h=6,
            text=value,
            border=0,
            dry_run=True,
            output="HEIGHT",
            wrapmode="CHAR"
        )

        row_height = max(
            label_height,
            value_height,
            6
        )

        # --------------------------------------
        # ตรวจว่าพื้นที่หน้าเหลือพอหรือไม่
        # --------------------------------------
        available_height = (
            pdf.h
            - pdf.b_margin
            - pdf.get_y()
        )

        if row_height > available_height:

            pdf.add_page()

            start_x = pdf.l_margin
            start_y = pdf.get_y()

        # --------------------------------------
        # พิมพ์ LABEL
        # --------------------------------------
        pdf.set_xy(
            start_x,
            start_y
        )

        pdf.multi_cell(
            w=LABEL_WIDTH,
            h=6,
            text=label,
            border=0,
            align="L",
            new_x=XPos.RIGHT,
            new_y=YPos.TOP,
            wrapmode="CHAR"
        )

        # --------------------------------------
        # พิมพ์ VALUE
        # --------------------------------------
        pdf.set_xy(
            start_x + LABEL_WIDTH,
            start_y
        )

        pdf.multi_cell(
            w=VALUE_WIDTH,
            h=6,
            text=value,
            border=0,
            align="L",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            wrapmode="CHAR"
        )

        # --------------------------------------
        # ปรับ Y ให้เท่ากับ row ที่สูงที่สุด
        # --------------------------------------
        pdf.set_y(
            start_y + row_height
        )

    # ==========================================
    # 7. HEADER
    # ==========================================
    set_font(21)
    
    pdf.multi_cell(
        w=PAGE_WIDTH,
        h=8,
        text="รายงานสรุปการประเมิน Asthma / COPD",
        border=0,
        align="C",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
        wrapmode="CHAR"
    )
    
    set_font(16)
    
    pdf.multi_cell(
        w=PAGE_WIDTH,
        h=7,
        text="คลินิกโรคปอด โรงพยาบาลวานรนิวาส",
        border=0,
        align="C",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
        wrapmode="CHAR"
    )
    
    # เส้นใต้ Header
    y = pdf.get_y()
    
    pdf.line(
        pdf.l_margin,
        y,
        pdf.w - pdf.r_margin,
        y
    )
    
    pdf.ln(3)
    # ==========================================
    # 8. Patient Information
    # ==========================================
    add_section_title(
        "ข้อมูลผู้ป่วย (Patient Information)"
    )

    add_secure_row(
        "เลขประจำตัวผู้ป่วย (HN):",
        data.get("hn")
        if data.get("hn")
        else "- ไม่ระบุ -"
    )

    add_secure_row(
        "ประเภทโรค (Disease):",
        data.get("disease", "-")
    )

    add_secure_row(
        "อายุ / เพศ:",
        f"{data.get('age', '-')} ปี / "
        f"{data.get('sex', '-')} "
        f"(BMI: {data.get('bmi', 0):.1f})"
    )

    add_secure_row(
        "ค่าเป้าหมายปอด (Predicted PEFR):",
        f"{data.get('pred_pefr', 0)} L/min"
    )

    pdf.ln(2)

    # ==========================================
    # 9. Symptoms & Tests
    # ==========================================
    add_section_title(
        "ข้อมูลการประเมินอาการ 4 สัปดาห์และการทดสอบ "
        "(Symptoms & Tests)"
    )

    add_secure_row(
        "อาการกลางวัน / กลางคืน:",
        f"{data.get('day_symp', '-')} / "
        f"{data.get('night_symp', '-')}"
    )

    add_secure_row(
        "ประวัติเข้า ER หรือ Admit:",
        f"ER {data.get('er_visit', 0)} ครั้ง / "
        f"Admit {data.get('admit_days', 0)} วัน"
    )

    add_secure_row(
        "ประวัติการสูบบุหรี่ (Smoking):",
        data.get("smoking", "-")
    )

    add_secure_row(
        "ลักษณะเสมหะ (Sputum):",
        data.get("sputum", "-")
    )

    add_secure_row(
        "คะแนนความเหนื่อยหอบ (mMRC):",
        data.get("mmrc", "-")
    )

    if "COPD" in data.get("disease", ""):

        add_secure_row(
            "คะแนน CAT Score:",
            f"{data.get('cat', 0)} คะแนน"
        )

    add_secure_row(
        "ระยะทางเดิน 6 นาที (6MWT):",
        f"{data.get('walk_dist', 0)} เมตร"
    )

    add_secure_row(
        "ออกซิเจนในเลือด (SpO2 Room Air):",
        f"{data.get('o2_sat', 0)} %"
    )

    pdf.ln(2)

    # ==========================================
    # 10. Clinical Assessment
    # ==========================================
    add_section_title(
        "ผลการประเมินทางคลินิก (Clinical Assessment)"
    )

    add_secure_row(
        "ระดับการควบคุมโรค (Control Level):",
        data.get("control", "-")
    )

    add_secure_row(
        "ความเสี่ยงกำเริบ (Exacerbation Risk):",
        data.get("risk", "-")
    )

    add_secure_row(
        "สมรรถภาพปอด (%Predicted PEFR):",
        f"{data.get('pct_pred', 0):.1f}% "
        f"(เป่าได้ {data.get('pre_pefr', 0)} L/min)"
    )

    add_secure_row(
        "ความร่วมมือในการใช้ยา (Adherence):",
        f"{data.get('adherence', 0)}%"
    )

    pdf.ln(2)

    # ==========================================
    # 11. Doctor's Summary
    # ==========================================
    add_section_title(
        "สรุปและคำแนะนำ (Doctor's Summary & Suggestions)"
    )

    suggestions = data.get(
        "suggestions",
        []
    )

    if suggestions:

        for sug in suggestions:

            set_font(15)

            pdf.multi_cell(
                w=PAGE_WIDTH,
                h=6,
                text=f"- {str(sug)}",
                border=0,
                align="L",
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
                wrapmode="CHAR"
            )

    else:

        set_font(15)

        pdf.multi_cell(
            w=PAGE_WIDTH,
            h=6,
            text="- ไม่มีคำแนะนำเพิ่มเติม",
            border=0,
            align="L",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            wrapmode="CHAR"
        )

    # ==========================================
    # 12. Signature
    # ==========================================
    pdf.ln(5)

    set_font(15)

    pdf.multi_cell(
        w=PAGE_WIDTH,
        h=6,
        text="ลงชื่อผู้ประเมิน.......................................................",
        border=0,
        align="R",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
        wrapmode="CHAR"
    )

    pdf.multi_cell(
        w=PAGE_WIDTH,
        h=6,
        text="วันที่........./........./.........",
        border=0,
        align="R",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
        wrapmode="CHAR"
    )

    # ==========================================
    # 12.5 FOOTER
    # ==========================================
    
    set_font(9)

    pdf.set_xy(
        pdf.l_margin,
        pdf.h - 6
    )
    
    pdf.cell(
        w=PAGE_WIDTH,
        h=5,
        text="ปรับปรุงวันที่ 17 กันยายน พ.ศ. 2569",
        border=0,
        align="L"
    )

    # ==========================================
    # 13. Save PDF
    # ==========================================
    tmp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )

    tmp_file.close()

    pdf.output(
        tmp_file.name
    )

    return tmp_file.name

# ==========================================
# UI หน้าเว็บหลัก
# ==========================================
st.title("🫁 Asthma/COPD Follow-up Dashboard")
st.markdown("ระบบบันทึกและประเมินผลการรักษาผู้ป่วยโรคทางเดินหายใจตีบ 🏥✨")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "👤 1. ข้อมูลทั่วไป", "🗣️ 2. ประเมินอาการ", "🫁 3. สมรรถภาพปอด", 
    "💊 4. การใช้ยา", "📊 5. CAT Score", "👨‍⚕️ สรุปสำหรับแพทย์"
])

if 'cat_score' not in st.session_state: st.session_state.cat_score = 0

with tab1:
    st.header("👤 ส่วนที่ 1: ข้อมูลทั่วไปและสัญญาณชีพ")
    col1, col2, col3 = st.columns(3)
    with col1:
        hn = st.text_input("เลขประจำตัวผู้ป่วย (HN) 🆔", placeholder="กรอกเลข HN เช่น 123456")
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
    
    st.subheader("ประวัติกำเริบ (Exacerbation)")
    col_ex1, col_ex2 = st.columns(2)
    with col_ex1: er_visit = st.number_input("🚑 จำนวนครั้งที่ไป ER (ครั้ง)", min_value=0, value=0)
    with col_ex2: admit_days = st.number_input("🏥 จำนวนวันที่ Admit (วัน)", min_value=0, value=0)
    
    st.subheader("อาการปัจจุบัน")
    col_cur1, col_cur2 = st.columns(2)
    with col_cur1: smoking = st.checkbox("ปัจจุบันยังสูบบุหรี่")
    with col_cur2: sputum = st.checkbox("มีเสมหะเหลือง/เขียว")
    
    mmrc_options = [
        "ระดับ 0: เหนื่อยเฉพาะเวลาออกกำลังกายหนัก ๆ เท่านั้น",
        "ระดับ 1: เหนื่อยเมื่อเดินเร็วบนทางราบ หรือเดินขึ้นเนินที่ไม่ชัน",
        "ระดับ 2: เดินบนทางราบได้ช้ากว่าคนวัยเดียวกัน หรือต้องหยุดพักเมื่อเดินปกติ",
        "ระดับ 3: ต้องหยุดพักหายใจหลังเดินไปได้ประมาณ 90-100 เมตร หรือเดินไม่กี่นาที",
        "ระดับ 4: เหนื่อยมากจนไม่ออกจากบ้าน หรือเหนื่อยแม้แต่ตอนแต่งตัว/ถอดเสื้อผ้า"
    ]
    mmrc_selected = st.selectbox("คะแนนประเมินความเหนื่อยหอบ (mMRC Score) 🚶‍♂️", mmrc_options)
    mmrc_score_only = mmrc_selected.split(":")[0]

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
        o2_sat = st.number_input("O2 Saturation Room Air (%)", min_value=0, max_value=100, value=98)
        if o2_sat < 90 and o2_sat > 0: st.error("🚨 ระวัง! SpO2 Room Air ต่ำกว่า 90%")

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
        st.info("ℹ️ ผู้ป่วยรายนี้เป็น Asthma ไม่จำเป็นต้องประเมิน CAT Score (ข้ามได้เลยครับ)")
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
    
    symptom_count = sum(1 for symp in [day_symp, night_symp, rescue_med] if not symp.startswith("0"))
    control_level = "Well Controlled (ควบคุมได้ดี)" if symptom_count == 0 else ("Partially Controlled (ควบคุมได้บางส่วน)" if symptom_count <= 2 else "Uncontrolled (ควบคุมไม่ได้)")
    risk_level = "High Risk (มีประวัติกำเริบ)" if (er_visit > 0 or admit_days > 0) else "Low Risk (ไม่มีประวัติกำเริบใน 4 สัปดาห์)"
    pct = (pre_pefr / pred_pefr * 100) if pred_pefr > 0 and pre_pefr > 0 else 0
    
    suggestions = []
    if adherence < 80: suggestions.append("ผู้ป่วยใช้ยาไม่สม่ำเสมอ แนะนำตรวจสอบสาเหตุและแก้ไขเทคนิคพ่นยา")
    if not edu3: suggestions.append("ยังไม่ได้ตรวจสอบเทคนิคพ่นยา ว่าถูกต้องหรือไม่")
    if smoking: suggestions.append("ผู้ป่วยยังสูบบุหรี่ ควรเน้นย้ำ Smoking Cessation")
    if "COPD" in disease_type and st.session_state.cat_score >= 10:
        suggestions.append(f"CAT Score สูง ({st.session_state.cat_score}) พิจารณาปรับยา หรือทำ Pulmonary Rehab")
    if er_visit > 0 or admit_days > 0:
        suggestions.append("มีประวัติ Exacerbation พิจารณา Step-up Therapy หรือ ICS/Oral Steroid")
    if not suggestions: suggestions.append("แนะนำให้การรักษาเดิม (Maintain current therapy) และติดตามอาการตามนัด")
    
    st.subheader(f"1. ระดับการควบคุม: {control_level}")
    st.subheader(f"2. ประวัติกำเริบ: {risk_level}")
    st.subheader("3. คำแนะนำ (Clinical Suggestions):")
    for s in suggestions: st.write(f"- {s}")
        
    st.markdown("---")
    st.subheader("📄 ส่งออกรายงาน (Export Report)")
    
    report_data = {
        "hn": hn,
        "disease": disease_type,
        "age": age,
        "sex": sex,
        "bmi": bmi,
        "pred_pefr": pred_pefr,
        "control": control_level,
        "risk": risk_level,
        "pre_pefr": pre_pefr,
        "pct_pred": pct,
        "adherence": adherence,
        "cat": st.session_state.cat_score,
        "suggestions": suggestions,
    
        "day_symp": day_symp,
        "night_symp": night_symp,
        "rescue_med": rescue_med,
        "er_visit": er_visit,
        "admit_days": admit_days,
    
        # ❗ ไม่มี emoji ใน PDF
        "smoking": "สูบบุหรี่" if smoking else "ไม่สูบ",
        "sputum": "มีเสมหะเหลือง/เขียว" if sputum else "ไม่มี",
    
        "mmrc": mmrc_score_only,
        "walk_dist": walk_dist,
        "o2_sat": o2_sat
    }
    
    filename_hn = hn.strip() if hn.strip() != "" else "No_HN"
    export_filename = f"Report_Asthma_COPD_HN_{filename_hn}.pdf"
    
    if st.button("🖨️ สร้างและดาวน์โหลดไฟล์ PDF (A4)", type="primary"):
        with st.spinner("กำลังจัดหน้ากระดาษและสร้าง PDF... ⏳"):
            try:
                if not os.path.exists("THSarabunNew.ttf"):
                    st.warning("⚠️ ไม่พบไฟล์ฟอนต์ 'THSarabunNew.ttf' ระบบจะใช้ฟอนต์ภาษาอังกฤษแทน ซึ่งอาจทำให้ภาษาไทยอ่านไม่ออก")
                    
                pdf_path = generate_pdf_report(report_data)
                
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label=f"📥 คลิกที่นี่เพื่อดาวน์โหลด (ชื่อไฟล์: {export_filename})",
                        data=pdf_file,
                        file_name=export_filename,
                        mime="application/pdf"
                    )
                st.success(f"✅ สร้างไฟล์ {export_filename} สำเร็จแล้ว!")
            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาด: {e}")
