import streamlit as st
import uuid
import pandas as pd
import datetime
import plotly.express as px
import unicodedata
import os
import calendar
from streamlit_gsheets import GSheetsConnection

# ==========================================
# CẤU HÌNH TRANG LÀM VIỆC
# ==========================================
st.set_page_config(page_title="Hệ thống Quản trị - Công an phường An Khánh", page_icon="☑️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; }
    .codx-header { background: linear-gradient(135deg, #005B9F 0%, #0078D7 100%); padding: 20px 30px; border-radius: 12px; color: white; margin-bottom: 25px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    .codx-title { font-size: 24px; font-weight: 700; margin: 0; }
    .codx-card { background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #EAECEF; }
    .login-box { max-width: 400px; margin: 80px auto; padding: 30px; background: white; border-radius: 12px; box-shadow: 0 8px 20px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #005B9F;}
    .divider-text { display: flex; align-items: center; text-align: center; color: #888; margin: 20px 0; }
    .divider-text::before, .divider-text::after { content: ''; flex: 1; border-bottom: 1px solid #eee; }
    .divider-text:not(:empty)::before { margin-right: .25em; }
    .divider-text:not(:empty)::after { margin-left: .25em; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. KHÓA VÒNG NGOÀI (Thay thế cho file run_app.bat)
# ==========================================
if "system_unlocked" not in st.session_state:
    st.session_state.system_unlocked = False

if not st.session_state.system_unlocked:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("### 🔒 XÁC THỰC HỆ THỐNG")
    st.markdown("<p style='color: gray;'>Vui lòng nhập mã bảo mật hệ thống để truy cập ứng dụng.</p>", unsafe_allow_html=True)
    
    sys_pwd = st.text_input("Mã bảo mật (App Key):", type="password")
    if st.button("Mở khóa ứng dụng 🔑", use_container_width=True, type="primary"):
        # Thay 'matkhauhethong' bằng mật khẩu bạn muốn dùng để mở app
        if sys_pwd == "matkhauhethong": 
            st.session_state.system_unlocked = True
            st.rerun()
        else:
            st.error("🚨 Mã xác thực hệ thống không đúng!")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop() # Dừng toàn bộ web nếu chưa qua cửa này

# ==========================================
# 2. MÀN HÌNH CHỌN QUYỀN (ADMIN / GUEST)
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None

if not st.session_state.logged_in:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    if os.path.exists("logo.png"): st.image("logo.png", width=80)
    st.markdown("### HỆ THỐNG QUẢN TRỊ")
    st.markdown("<p style='color: gray; margin-bottom: 20px;'>Công an phường An Khánh</p>", unsafe_allow_html=True)
    
    if st.button("👁️ Truy cập chế độ Khách (Chỉ xem)", use_container_width=True):
        st.session_state.logged_in = True
        st.session_state.role = "Guest"
        st.rerun()
    
    st.markdown('<div class="divider-text">hoặc dành cho nội bộ</div>', unsafe_allow_html=True)
    
    pwd = st.text_input("Mật khẩu Quản trị viên:", type="password", placeholder="Nhập mật khẩu...")
    if st.button("Đăng nhập Admin 🚀", use_container_width=True, type="primary"):
        if pwd == "123":
            st.session_state.logged_in = True
            st.session_state.role = "Admin"
            st.rerun()
        else:
            st.error("🚨 Sai mật khẩu! Vui lòng thử lại.")
            
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 3. KẾT NỐI GOOGLE SHEETS VÀ TẢI DỮ LIỆU
# ==========================================
# >>> ĐIỀN LINK GOOGLE SHEETS CỦA BẠN VÀO ĐÂY: <<<
SPREADSHEET_URL = "URL_GOOGLE_SHEETS_CUA_BAN" 

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
        # Lấy từ cột B đến F (tương ứng index 1 đến 5 trong gsheets)
        df = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="Data", usecols=[1, 2, 3, 4, 5])
        df.columns = ["TEN_BAO_CAO", "KY_BAO_CAO", "DEADLINE", "TRANG_THAI_GOC", "DON_VI_YEU_CAU"]
        df = df.dropna(subset=['TEN_BAO_CAO'])
        df['KY_BAO_CAO'] = df['KY_BAO_CAO'].fillna("Không xác định")
        df['DEADLINE'] = pd.to_datetime(df['DEADLINE'], errors='coerce')
        df['TRANG_THAI_GOC'] = df['TRANG_THAI_GOC'].fillna("Chưa xử lý")
        df['DON_VI_YEU_CAU'] = df['DON_VI_YEU_CAU'].fillna("Không xác định")
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
# 4. GIAO DIỆN HEADER & BỘ LỌC TÌM KIẾM
# ==========================================
col_l, col_r = st.columns([1, 8])
with col_l:
    if os.path.exists("logo.png"): st.image("logo.png", width=90)
    else: st.write("📌 **LOGO**")

with col_r:
    role_text = "Quản trị viên (Admin)" if st.session_state.role == "Admin" else "Khách (Chỉ xem)"
    st.markdown(f"""
    <div class="codx-header">
        <p class="codx-title">☑️ HỆ THỐNG QUẢN TRỊ CÔNG VIỆC CÔNG AN PHƯỜNG AN KHÁNH</p>
        <p style="margin:0; opacity:0.8;">Cập nhật trạng thái, theo dõi tiến độ và lịch báo cáo. Quyền truy cập: <b>{role_text}</b></p>
    </div>
    """, unsafe_allow_html=True)

if st.sidebar.button("🚪 Thoát / Đổi quyền", type="primary"):
    st.session_state.clear()
    st.rerun()

with st.sidebar:
    st.header("🔍 BỘ LỌC TÌM KIẾM")
    txt_search = st.text_input("Tên báo cáo:")
    
    ky_list = st.session_state.df_master['KY_BAO_CAO'].unique().tolist()
    all_kys = set([k for ky in ky_list if isinstance(ky, str) for k in ky.split(", ")])
    sel_ky = st.multiselect("Lọc theo Kỳ:", list(all_kys), default=list(all_kys))
    
    thang_list = sorted([m for m in st.session_state.df_master['THANG'].unique() if m != 0])
    sel_thang = st.multiselect("Lọc theo Tháng:", options=thang_list + [0], default=thang_list + [0], format_func=lambda