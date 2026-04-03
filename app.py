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
# C?U HÌNH TRANG
# ==========================================
st.set_page_config(
    page_title="H? th?ng Qu?n tr? - CA An Khánh", 
    page_icon="??", 
    layout="wide"
)

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
# 1. KHÓA B?O M?T H? TH?NG
# ==========================================
if "system_unlocked" not in st.session_state:
    st.session_state.system_unlocked = False

if not st.session_state.system_unlocked:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("### ?? XÁC TH?C H? TH?NG")
    st.markdown("<p style='color:gray;'>Nh?p mã b?o m?t d? vào app.</p>", unsafe_allow_html=True)
    
    sys_pwd = st.text_input("Mã b?o m?t:", type="password")
    if st.button("M? khóa ??", use_container_width=True, type="primary"):
        if sys_pwd == "matkhauhethong": 
            st.session_state.system_unlocked = True
            st.rerun()
        else:
            st.error("?? Sai mã b?o m?t!")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 2. CH?N QUY?N (ADMIN / GUEST)
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None

if not st.session_state.logged_in:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    if os.path.exists("logo.png"): 
        st.image("logo.png", width=80)
    st.markdown("### H? TH?NG QU?N TR?")
    st.markdown("<p style='color:gray;'>Công an phu?ng An Khánh</p>", unsafe_allow_html=True)
    
    if st.button("??? Truy c?p Khách (Ch? xem)", use_container_width=True):
        st.session_state.logged_in = True
        st.session_state.role = "Guest"
        st.rerun()
    
    st.markdown('<div class="divider-text">N?i b?</div>', unsafe_allow_html=True)
    
    pwd = st.text_input("M?t kh?u Admin:", type="password")
    if st.button("Ðang nh?p Admin ??", use_container_width=True, type="primary"):
        if pwd == "123":
            st.session_state.logged_in = True
            st.session_state.role = "Admin"
            st.rerun()
        else:
            st.error("?? Sai m?t kh?u!")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 3. K?T N?I GSHEETS & T?I D? LI?U
# ==========================================
SPREADSHEET_URL = "URL_GOOGLE_SHEETS_CUA_BAN" 

conn = st.connection("gsheets", type=GSheetsConnection)
today = pd.Timestamp.today().normalize()

def phan_loai(row):
    tt = str(row['TRANG_THAI_GOC']).upper()
    tt_norm = unicodedata.normalize('NFKD', tt).encode('ascii', 'ignore').decode('ascii')
    
    if "HOAN THANH" in tt_norm: return "? HOÀN THÀNH"
    if pd.isna(row['DEADLINE']): return "? ÐANG TH?C HI?N"
        
    days_diff = (row['DEADLINE'] - today).days
    if days_diff < 0: return "?? TR? H?N"
    if 0 <= days_diff <= 5: return "?? C?N LÀM G?P"
    return "? ÐANG TH?C HI?N"

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
        
        # Ði?n giá tr? m?c d?nh tránh l?i
        df['KY_BAO_CAO'] = df['KY_BAO_CAO'].fillna("Không xác d?nh")
        df['TRANG_THAI_GOC'] = df['TRANG_THAI_GOC'].fillna("Chua x? lý")
        df['DON_VI_YEU_CAU'] = df['DON_VI_YEU_CAU'].fillna("Không xác d?nh")
        
        # X? lý th?i gian
        df['DEADLINE'] = pd.to_datetime(df['DEADLINE'], errors='coerce')
        df['THANG'] = df['DEADLINE'].dt.month.fillna(0).astype(int)
        
        # Ðánh giá c?nh báo
        df['CANH_BAO'] = df.apply(phan_loai, axis=1)
        df['_ID'] = range(len(df))
        return df
    except Exception as e:
        st.error(f"? L?I Ð?C GOOGLE SHEETS: {e}")
        st.stop()

if "df_master" not in st.session_state:
    st.session_state.df_master = load_data()
if "editor_key" not in st.session_state:
    st.session_state.editor_key = str(uuid.uuid4())

# ==========================================
# 4. GIAO DI?N HEADER & B? L?C
# ==========================================
col_l, col_r = st.columns([1, 8])
with col_l:
    if os.path.exists("logo.png"): st.image("logo.png", width=90)
    else: st.write("?? **LOGO**")

with col_r:
    r_txt = "Admin" if st.session_state.role == "Admin" else "Khách (Ch? xem)"
    st.markdown(f"""
    <div class="codx-header">
        <p class="codx-title">?? QU?N TR? CÔNG VI?C CÔNG AN PHU?NG AN KHÁNH</p>
        <p style="margin:0;">Quy?n truy c?p: <b>{r_txt}</b></p>
    </div>
    """, unsafe_allow_html=True)

if st.sidebar.button("?? Thoát / Ð?i quy?n", type="primary"):
    st.session_state.clear()
    st.rerun()

with st.sidebar:
    st.header("?? B? L?C")
    txt_search = st.text_input("Tên báo cáo:")
    
    # L?c K?
    k_list = st.session_state.df_master['KY_BAO_CAO'].unique().tolist()
    all_k = set([k for ky in k_list if isinstance(ky, str) for k in ky.split(", ")])
    sel_ky = st.multiselect("L?c K?:", list(all_k), default=list(all_k))
    
    # L?c Tháng
    t_list = sorted([m for m in st.session_state.df_master['THANG'].unique() if m != 0])
    t_opts = t_list + [0]
    
    def fmt_m(x):
        return f"Tháng {x}" if x != 0 else "Chua có h?n"

    sel_thang = st.multiselect("L?c Tháng:", options=t_opts, default=t_opts, format_func=fmt_m)
    
    # L?c Tr?ng thái & Ðon v?
    tt_opts = ["?? TR? H?N", "?? C?N LÀM G?P", "? ÐANG TH?C HI?N", "? HOÀN THÀNH"]
    sel_tt = st.multiselect("Tr?ng thái:", tt_opts, default=tt_opts)

    dv_opts = st.session_state.df_master['DON_VI_YEU_CAU'].unique().tolist()
    sel_dv = st.multiselect("Ðon v? yêu c?u:", dv_opts, default=dv_opts)