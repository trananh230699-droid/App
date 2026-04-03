import streamlit as st
import uuid
import pandas as pd
import datetime
import plotly.express as px
import unicodedata
import os
import calendar
import time
from streamlit_gsheets import GSheetsConnection

# ==========================================
# CẤU HÌNH TRANG
# ==========================================
st.set_page_config(
    page_title="Hệ thống Quản trị - CAP An Khánh", 
    page_icon="☑️", 
    layout="wide"
)

# ==========================================
# GIAO DIỆN HIỆN ĐẠI, DỄ NHÌN, ĐẬM CHẤT CYBER (CYBER THEME)
# ==========================================
cyber_css = """
    <style>
    /* Tổng thể màn hình dark mode, chữ xanh lá terminal */
    .stApp { background-color: #050505; color: #33ff33; font-family: 'Consolas', 'Courier New', monospace; }
    
    /* Cấu trúc header đậm chất công nghệ */
    .codx-header { 
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%); 
        padding: 15px 25px; 
        border-radius: 8px; 
        color: #33ff33; 
        margin-bottom: 25px; 
        box-shadow: 0 2px 10px rgba(51, 255, 51, 0.2); 
        border: 1px solid #33ff33;
    }
    .codx-title { font-size: 22px; font-weight: 700; margin: 0; text-shadow: 0 0 10px #33ff33;}
    
    /* Thẻ card cho bảng và biểu đồ */
    .codx-card { 
        background-color: #0f0f0f; 
        padding: 20px; 
        border-radius: 8px; 
        box-shadow: 0 2px 8px rgba(51, 255, 51, 0.1); 
        border: 1px solid #1a1a1a; 
    }
    
    /* Giao diện khung đăng nhập/xác thực */
    .login-box { 
        max-width: 450px; 
        margin: 60px auto; 
        padding: 30px; 
        background: #0f0f0f; 
        border-radius: 10px; 
        box-shadow: 0 5px 20px rgba(51, 255, 51, 0.25); 
        text-align: center; 
        border: 2px solid #33ff33;
    }
    
    /* Tùy chỉnh input text đậm chất hack */
    .stTextInput input {
        background-color: #000 !important;
        color: #33ff33 !important;
        border: 1px solid #33ff33 !important;
        font-family: 'Consolas', monospace !important;
        font-size: 16px !important;
        letter-spacing: 2px;
        text-align: center;
    }
    
    /* Tùy chỉnh button */
    .stButton>button {
        background-color: #0f0f0f;
        color: #33ff33;
        border: 1px solid #33ff33;
        font-family: 'Consolas', monospace;
        font-weight: bold;
        transition: 0.3s;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #33ff33;
        color: #000;
        box-shadow: 0 0 15px #33ff33;
    }
    
    /* Hiệu ứng loading terminal */
    .terminal-load {
        font-family: 'Consolas', monospace;
        color: #33ff33;
        font-size: 14px;
        line-height: 1.6;
        background: #000;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #1a1a1a;
        margin-bottom: 20px;
        text-align: left;
    }
    
    /* Ẩn bớt các element thừa của Streamlit cho pro */
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(cyber_css, unsafe_allow_html=True)

# ==========================================
# XỬ LÝ PHIÊN ĐĂNG NHẬP (F5 CHỐNG MẤT LOG)
# ==========================================
# Lấy quyền từ URL parameter (để giữ phiên khi F5)
current_auth_param = st.query_params.get("authenticated", "false")

if "system_authenticated" not in st.session_state:
    st.session_state.system_authenticated = (current_auth_param == "true")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = st.session_state.system_authenticated

# ==========================================
# 1. MÀN HÌNH YÊU CẦU NHẬP MÃ ĐĂNG NHẬP ĐỂ TRUY CẬP
# ==========================================
if not st.session_state.system_authenticated:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    
    # Logo gấp đôi so với hợp lý, nằm ở giữa (width=240)
    col_logo1, col_logo2, col_logo3 = st.columns([1, 1.5, 1])
    with col_logo2:
        if os.path.exists("logo.png"): 
            st.image("logo.png", width=300) # Logo gấp đôi
            
    st.markdown("### 🖥️ HỆ THỐNG GIÁM SÁT AN NINH MẠNG")
    st.markdown("<p style='color:#33ff33; opacity:0.7;'>Vui lòng nhập mã TAC CHIEN để truy cập</p>", unsafe_allow_html=True)
    
    with st.form("system_auth_form"):
        # Nhập mã đăng nhập
        sys_pwd = st.text_input("MÃ ĐĂNG NHẬP:", type="password")
        submit_auth = st.form_submit_button("XÁC THỰC QUYỀN TRUY CẬP")
        
        if submit_auth:
            if sys_pwd == "CY": # Mã đăng nhập Tac Chien
                # HIỆU ỨNG LOADING KIỂU HACKER, CÓ %, TẦM 3 GIÂY, CHUYÊN NGHIỆP
                auth_placeholder = st.empty()
                with auth_placeholder.container():
                    st.markdown('<div class="terminal-load">', unsafe_allow_html=True)
                    lines = [
                        "> Initializing secure protocol...",
                        "> Verifying credentials against central node...",
                        "> Token decrypted: [CY-OPS-404x1]",
                        "> Injecting security parameters...",
                        "> Connection established via port 8501."
                    ]
                    load_text = ""
                    for line in lines:
                        load_text += line + "<br>"
                        st.markdown(load_text, unsafe_allow_html=True)
                        time.sleep(0.3) # 0.3 * 5 = 1.5 giây hiện chữ
                    
                    # Chạy % tầm 1.5 giây
                    for percent in range(0, 101, 20):
                        time.sleep(0.3)
                        pct_text = f"> LOADING SYSTEM DATABASE... {percent}%"
                        st.markdown(load_text + pct_text, unsafe_allow_html=True)
                        
                    st.markdown(load_text + "> LOADING SYSTEM DATABASE... 100%<br>> ACCESS GRANTED. WELCOME COMANDANTE.", unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    time.sleep(0.5)
                
                # Hoàn tất xác thực và lưu phiên F5
                st.session_state.system_authenticated = True
                st.session_state.logged_in = True
                st.query_params["authenticated"] = "true" # Lưu param F5 chống mất
                auth_placeholder.empty()
                st.rerun()
            else:
                st.error("🚨 Mã Đăng nhập không chính xác! Truy cập bị từ chối.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 2. GIAO DIỆN CHÍNH THỨC SAU KHI ĐĂNG NHẬP
# ==========================================
# Ghi đè lại CSS Terminal sang CSS làm việc chuyên nghiệp (vẫn giữCyber)
cyber_work_css = """
    <style>
    /* Tổng thể màn hình dark mode, chữ xanh lá terminal */
    .stApp { background-color: #050505; color: #33ff33; font-family: 'Consolas', 'Courier New', monospace; }
    
    /* Cấu trúc header đậm chất công nghệ */
    .codx-header { 
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%); 
        padding: 15px 25px; 
        border-radius: 8px; 
        color: #33ff33; 
        margin-bottom: 25px; 
        box-shadow: 0 2px 10px rgba(51, 255, 51, 0.2); 
        border: 1px solid #33ff33;
    }
    .codx-title { font-size: 22px; font-weight: 700; margin: 0; text-shadow: 0 0 10px #33ff33;}
    
    /* Thẻ card cho bảng và biểu đồ */
    .codx-card { 
        background-color: #0f0f0f; 
        padding: 20px; 
        border-radius: 8px; 
        box-shadow: 0 2px 8px rgba(51, 255, 51, 0.1); 
        border: 1px solid #1a1a1a; 
    }
    
    /* Tùy chỉnh input text trong bảng về dạng chuyên nghiệp */
    .stTextInput input {
        background-color: #000 !important;
        color: #33ff33 !important;
        border: 1px solid #1a1a1a !important;
        font-family: 'Consolas', monospace !important;
        font-size: 14px !important;
        letter-spacing: 0px;
        text-align: left;
    }
    .stTextInput input:focus {
        border-color: #33ff33 !important;
        box-shadow: 0 0 5px #33ff33 !important;
    }
    
    /* Tùy chỉnh button trong bảng */
    .stButton>button {
        background-color: #0f0f0f;
        color: #33ff33;
        border: 1px solid #1a1a1a;
        font-family: 'Consolas', monospace;
        font-weight: bold;
        transition: 0.3s;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #33ff33;
        color: #000;
        box-shadow: 0 0 15px #33ff33;
    }
    
    /* Ẩn bớt các element thừa của Streamlit cho pro */
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(cyber_work_css, unsafe_allow_html=True)

# ==========================================
# 3. KẾT NỐI GSHEETS & TẢI DỮ LIỆU
# ==========================================
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1WNXCatSajRif42atvJ9B2tqG7gHlLkQVfXVN-FpUdi8/edit?gid=2004413414#gid=2004413414&fvid=58293819" 

conn = st.connection("gsheets", type=GSheetsConnection)
today = pd.Timestamp.today().normalize()

def phan_loai(row):
    tt = str(row['TRANG_THAI_GOC']).upper()
    tt_norm = unicodedata.normalize('NFKD', tt).encode('ascii', 'ignore').decode('ascii')
    
    if "HOAN THANH" in tt_norm: return "✅ HOÀN THÀNH"
    if pd.isna(row['DEADLINE']): return "⏳ ĐANG THỰC HIỆN"
        
    days_diff = (row['DEADLINE'] - today).days
    if days_diff < 0: return "🚨 TRỄ HẠN"
    if 0 <= days_diff <= 5: return "🔥 CẦN LÀM GẤP"
    return "⏳ ĐANG THỰC HIỆN"

@st.cache_data(ttl=10)
def load_data():
    try:
        df = conn.read(
            spreadsheet=SPREADSHEET_URL, 
            worksheet="Data", 
            usecols=[1, 2, 3, 4, 5]
        )
        df.columns = [
            "TEN_BAO_CAO", "KY_BAO_CAO", "DEADLINE", 
            "TRANG_THAI_GOC", "DON_VI_YEU_CAU"
        ]
        df = df.dropna(subset=['TEN_BAO_CAO'])
        df['KY_BAO_CAO'] = df['KY_BAO_CAO'].fillna("Không xác định")
        df['TRANG_THAI_GOC'] = df['TRANG_THAI_GOC'].fillna("Chưa xử lý")
        df['DON_VI_YEU_CAU'] = df['DON_VI_YEU_CAU'].fillna("Không xác định")
        df['DEADLINE'] = pd.to_datetime(df['DEADLINE'], errors='coerce')
        df['THANG'] = df['DEADLINE'].dt.month.fillna(0).astype(int)
        df['CANH_BAO'] = df.apply(phan_loai, axis=1)
        df['_ID'] = range(len(df))
        return df
    except Exception as e:
        st.error(f"❌ LỖI: Không thể đọc Google Sheets. Chi tiết: {e}")
        st.stop()

if "df_master" not in st.session_state:
    st.session_state.df_master = load_data()
if "editor_key" not in st.session_state:
    st.session_state.editor_key = str(uuid.uuid4())

# ==========================================
# 4. GIAO DIỆN HEADER & BỘ LỌC TÌM KIẾM (KHÔNG THAY ĐỔI)
# ==========================================
col_l, col_r = st.columns([1, 8])
with col_l:
    if os.path.exists("logo.png"): 
        st.image("logo.png", width=120) # Logo nhỏ gọn trên header
    else: 
        st.write("📌 **LOGO**")

with col_r:
    st.markdown(f"""
    <div class="codx-header">
        <p class="codx-title">☑️ HỆ THỐNG QUẢN TRỊ CÔNG VIỆC CÔNG AN PHƯỜNG AN KHÁNH</p>
        <p style="margin:0; opacity:0.8;">Cập nhật trạng thái Tac Chien, theo dõi tiến độ báo cáo.</p>
    </div>
    """, unsafe_allow_html=True)

# Đăng xuất xóa Query Param để bắt đăng nhập lại
if st.sidebar.button("🚪 Đăng xuất hệ thống", type="primary"):
    st.query_params.clear() # Xóa URL param authenticated
    st.session_state.clear()
    st.rerun()

with st.sidebar:
    st.header("🔍 BỘ LỌC TÌM KIẾM")
    txt_search = st.text_input("Tên báo cáo:")
    
    ky_list = st.session_state.df_master['KY_BAO_CAO'].unique().tolist()
    all_kys = set([k for ky in ky_list if isinstance(ky, str) for k in ky.split(", ")])
    sel_ky = st.multiselect("Lọc theo Kỳ:", list(all_kys), default=list(all_kys))
    
    thang_list = sorted([m for m in st.session_state.df_master['THANG'].unique() if m != 0])
    thang_options = thang_list + [0]
    
    def format_thang_func(x):
        return f"Tháng {x}" if x != 0 else "Chưa có hạn nộp"

    sel_thang = st.multiselect("Lọc theo Tháng:", options=thang_options, default=thang_options, format_func=format_thang_func)
    
    tt_list = ["🚨 TRỄ HẠN", "🔥 CẦN LÀM GẤP", "⏳ ĐANG THỰC HIỆN", "✅ HOÀN THÀNH"]
    sel_tt = st.multiselect("Lọc Trạng thái:", tt_list, default=tt_list)

    dv_list = st.session_state.df_master['DON_VI_YEU_CAU'].unique().tolist()
    sel_dv = st.multiselect("Lọc Đơn vị yêu cầu:", dv_list, default=dv_list)
    
    st.divider()
    if st.button("🔄 Làm mới dữ liệu", use_container_width=True):
        st.cache_data.clear()
        st.session_state.df_master = load_data() 
        st.rerun()

def check_ky(row_ky):
    if not sel_ky: return False
    return any(k in str(row_ky) for k in sel_ky)

mask = (
    st.session_state.df_master['TEN_BAO_CAO'].str.contains(txt_search, case=False, na=False) &
    st.session_state.df_master['KY_BAO_CAO'].apply(check_ky) &
    st.session_state.df_master['THANG'].isin(sel_thang) &
    st.session_state.df_master['CANH_BAO'].isin(sel_tt) &
    st.session_state.df_master['DON_VI_YEU_CAU'].isin(sel_dv)
)
df_filtered = st.session_state.df_master[mask].copy()

# ==========================================
# 5. BẢNG CÔNG VIỆC CHI TIẾT (KHÔNG THAY ĐỔI)
# ==========================================
metric_container = st.container()
st.markdown("<br>", unsafe_allow_html=True)
col_main, col_sub = st.columns([2.4, 1.0])

with col_main:
    st.markdown('<div class="codx-card">', unsafe_allow_html=True)
    st.subheader("📋 BẢNG CÔNG VIỆC CHI TIẾT")
    
    df_filtered = df_filtered.sort_values(by='DEADLINE', ascending=True, na_position='last').reset_index(drop=True)
    df_filtered.insert(0, "🗑️ Xóa", False)

    cauhinh_cot = {
        "_ID": None, 
        "🗑️ Xóa": st.column_config.CheckboxColumn("Xóa", default=False, width="small"),
        "TEN_BAO_CAO": st.column_config.TextColumn("Tên công việc", width="large"), 
        "KY_BAO_CAO": st.column_config.TextColumn("Kỳ báo cáo"), 
        "DEADLINE": st.column_config.DateColumn("Hạn chót", format="DD/MM/YYYY"),
        "TRANG_THAI_GOC": st.column_config.SelectboxColumn("Trạng thái", options=["Chưa xử lý", "Đang thực hiện", "Hoàn thành"]),
        "CANH_BAO": st.column_config.TextColumn("Tình trạng", disabled=True),
        "DON_VI_YEU_CAU": st.column_config.TextColumn("Đơn vị yêu cầu")
    }

    edited_df = st.data_editor(
        df_filtered,
        key=st.session_state.editor_key,
        use_container_width=True, 
        hide_index=True, 
        num_rows="dynamic",
        column_config=cauhinh_cot
    )

    deleted_ids = edited_df[edited_df["🗑️ Xóa"] == True]["_ID"].tolist()
    if deleted_ids:
        st.session_state.df_master = st.session_state.df_master[~st.session_state.df_master["_ID"].isin(deleted_ids)]
        st.rerun() 
        
    edited_df = edited_df[edited_df["🗑️ Xóa"] == False]
    for _, row in edited_df.iterrows():
        m_idx = st.session_state.df_master.index[st.session_state.df_master['_ID'] == row['_ID']].tolist()[0]
        st.session_state.df_master.at[m_idx, 'TEN_BAO_CAO'] = row['TEN_BAO_CAO']
        st.session_state.df_master.at[m_idx, 'KY_BAO_CAO'] = row['KY_BAO_CAO']
        st.session_state.df_master.at[m_idx, 'DEADLINE'] = row['DEADLINE']
        st.session_state.df_master.at[m_idx, 'TRANG_THAI_GOC'] = row['TRANG_THAI_GOC']
        st.session_state.df_master.at[m_idx, 'DON_VI_YEU_CAU'] = row['DON_VI_YEU_CAU']
        st.session_state.df_master.at[m_idx, 'CANH_BAO'] = phan_loai(row)

    if st.button("💾 LƯU LÊN CLOUD", type="primary"):
        conn.update(worksheet="Data", data=st.session_state.df_master[["TEN_BAO_CAO", "KY_BAO_CAO", "DEADLINE", "TRANG_THAI_GOC", "DON_VI_YEU_CAU"]])
        st.success("✅ Đã cập nhật dữ liệu thành công lên Google Sheets!")
        st.cache_data.clear()
        st.session_state.df_master = load_data()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 6. BIỂU ĐỒ & LỊCH NHẮC VIỆC (KHÔNG THAY ĐỔI)
# ==========================================
with metric_container:
    c_m1, c_m2, c_m3 = st.columns(3)
    total = len(df_filtered)
    done = len(df_filtered[df_filtered['CANH_BAO'] == "✅ HOÀN THÀNH"])
    late = len(df_filtered[df_filtered['CANH_BAO'] == "🚨 TRỄ HẠN"])
    
    tyle_hoanthanh = round(done/total*100) if total > 0 else 0
    
    with c_m1: st.metric("TỔNG CÔNG VIỆC", total)
    with c_m2: st.metric("ĐÃ XONG", done, f"{tyle_hoanthanh}%")
    with c_m3: st.metric("TRỄ HẠN", late, delta_color="inverse", delta="Cảnh báo")

with col_sub:
    st.markdown('<div class="codx-card">', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-weight:bold;'>📊 TỶ LỆ TIẾN ĐỘ</p>", unsafe_allow_html=True)
    
    bang_mau_bieudo = {
        "✅ HOÀN THÀNH": "#10B981", # Xanh lá
        "🚨 TRỄ HẠN": "#EF4444",    # Đỏ
        "⏳ ĐANG THỰC HIỆN": "#3B82F6", # Xanh dương
        "🔥 CẦN LÀM GẤP": "#F59E0B"   # Cam
    }
    
    if total > 0:
        fig = px.pie(
            df_filtered, 
            names='CANH_BAO', 
            hole=0.5,
            color='CANH_BAO',
            color_discrete_map=bang_mau_bieudo
        )
        fig.update_layout(showlegend=False, height=200, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div><br>', unsafe_allow_html=True)

    st.markdown('<div class="codx-card">', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-weight:bold;'>📅 LỊCH NHẮC VIỆC THÁNG NÀY</p>", unsafe_allow_html=True)
    
    now = datetime.datetime.now()
    cal = calendar.monthcalendar(now.year, now.month)
    df_chua_xong = df_filtered[df_filtered['CANH_BAO'] != "✅ HOÀN THÀNH"].copy()
    df_chua_xong_month = df_chua_xong[df_chua_xong['DEADLINE'].dt.month == now.month]
    deadlines = df_chua_xong_month['DEADLINE'].dt.day.dropna().astype(int).unique().tolist()

    html_cal = '<table style="width:100%; border-collapse: collapse; font-size:13px; text-align:center;">'
    html_cal += '<tr><th style="color:red">CN</th><th>T2</th><th>T3</th><th>T4</th><th>T5</th><th>T6</th><th>T7</th></tr>'
    
    for week in cal:
        html_cal += '<tr>'
        for day in week:
            if day == 0: 
                html_cal += '<td></td>'
            elif day == now.day: 
                html_cal += f'<td style="background-color:rgba(51, 255, 51, 0.3); border-radius:50%; font-weight:bold; color:#fff;">{day}</td>'
            elif day in deadlines: 
                html_cal += f'<td style="background-color:#EF4444; border-radius:50%; font-weight:bold; color:#fff;">{day}</td>'
            else: 
                html_cal += f'<td>{day}</td>'
        html_cal += '</tr>'
    html_cal += '</table>'
    st.markdown(html_cal, unsafe_allow_html=True)
    st.caption("🔴 Đỏ: Hạn nộp báo cáo - 🟢 Xanh: Hôm nay")
    st.markdown('</div>', unsafe_allow_html=True)