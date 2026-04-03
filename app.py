import streamlit as st
import uuid
import pandas as pd
import datetime
import plotly.express as px
import unicodedata
import os
import calendar
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Hệ thống Quản trị - Công an phường An Khánh", page_icon="☑️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; }
    .codx-header { background: linear-gradient(135deg, #005B9F 0%, #0078D7 100%); padding: 20px 30px; border-radius: 12px; color: white; margin-bottom: 25px;}
    .codx-title { font-size: 24px; font-weight: 700; margin: 0; }
    .codx-card { background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #EAECEF; }
    .login-box { max-width: 400px; margin: 80px auto; padding: 30px; background: white; border-radius: 12px; box-shadow: 0 8px 20px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #005B9F;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# KHÓA VÒNG NGOÀI (Thay thế cho file run_app.bat)
# ==========================================
def check_system_password():
    if "system_unlocked" not in st.session_state:
        st.session_state.system_unlocked = False

    if not st.session_state.system_unlocked:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("### 🔒 XÁC THỰC HỆ THỐNG")
        st.markdown("<p style='color: gray;'>Vui lòng nhập mã bảo mật hệ thống để truy cập ứng dụng.</p>", unsafe_allow_html=True)
        
        sys_pwd = st.text_input("Mã bảo mật (App Key):", type="password")
        if st.button("Mở khóa ứng dụng 🔑", use_container_width=True, type="primary"):
            # MẬT KHẨU HỆ THỐNG Ở ĐÂY (thay thế cho pass ở CMD lúc chạy bat)
            if sys_pwd == "matkhauhethong": 
                st.session_state.system_unlocked = True
                st.rerun()
            else:
                st.error("🚨 Mã xác thực hệ thống không đúng!")
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop() # Dừng toàn bộ web nếu chưa qua cửa này

check_system_password() # Chạy hàm kiểm tra

# ==========================================
# KHỞI TẠO SESSION & MÀN HÌNH ĐĂNG NHẬP GUEST/ADMIN
# ==========================================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "role" not in st.session_state: st.session_state.role = None

if not st.session_state.logged_in:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("### HỆ THỐNG QUẢN TRỊ\nCông an phường An Khánh")
    if st.button("👁️ Truy cập chế độ Khách (Chỉ xem)", use_container_width=True):
        st.session_state.logged_in = True; st.session_state.role = "Guest"; st.rerun()
    st.markdown("<hr>", unsafe_allow_html=True)
    pwd = st.text_input("Mật khẩu Quản trị viên:", type="password")
    if st.button("Đăng nhập Admin 🚀", use_container_width=True, type="primary"):
        if pwd == "123":
            st.session_state.logged_in = True; st.session_state.role = "Admin"; st.rerun()
        else: st.error("🚨 Sai mật khẩu!")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# HÀM TẢI & XỬ LÝ DỮ LIỆU TỪ GOOGLE SHEETS
# ==========================================
# ĐIỀN LINK GOOGLE SHEETS CỦA BẠN VÀO ĐÂY:
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1mjQru6IcW-r1vfqOgGUt8IJ5OtAYiDut/edit?gid=2004413414#gid=2004413414&fvid=58293819" 

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

@st.cache_data(ttl=5)
def load_data():
    try:
        # Lấy từ cột B đến F (tương ứng index 1 đến 5)
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

if "df_master" not in st.session_state: st.session_state.df_master = load_data()
if "editor_key" not in st.session_state: st.session_state.editor_key = str(uuid.uuid4())

# (Từ đây trở xuống, giữ nguyên hoàn toàn các hàm Giao diện, Bộ lọc, Xóa tạm như cũ...)
# (Để tiết kiệm không gian, bạn ghép phần Sidebar, Hiển thị bảng, Sắp xếp, Biểu đồ từ đoạn code trước vào đây)

# CHỈ SỬA LẠI ĐOẠN LƯU VĨNH VIỄN NHƯ SAU:
# ... (Trong phần Admin) ...
        with col_save:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if st.button("💾 XÁC NHẬN LƯU LÊN CLOUD", type="primary", use_container_width=True):
                if del_pwd == "123":
                    try:
                        df_to_save = st.session_state.df_master[["TEN_BAO_CAO", "KY_BAO_CAO", "DEADLINE", "TRANG_THAI_GOC", "DON_VI_YEU_CAU"]]
                        # Ghi đè vào Google Sheets thay vì Excel
                        conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Data", data=df_to_save)
                        st.success("✅ Đã chốt hạ thành công lên Google Sheets!")
                        st.cache_data.clear()
                        st.session_state.df_master = load_data()
                        st.rerun()
                    except Exception as e:
                        st.error(f"🚨 LỖI khi lưu lên Cloud: {e}")
                else:
                    st.error("🚨 Sai mật khẩu! Không thể ghi dữ liệu.")