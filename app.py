import streamlit as st
import streamlit.components.v1 as components
import uuid
import pandas as pd
import datetime
import plotly.express as px
import unicodedata
import os
import calendar
import time
import json
import random
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
# ĐỒNG BỘ MÚI GIỜ VIỆT NAM (UTC+7)
# ==========================================
def get_vn_time():
    return datetime.datetime.utcnow() + datetime.timedelta(hours=7)

# ==========================================
# HỆ THỐNG GHI LOG (LỊCH SỬ TRUY CẬP)
# ==========================================
LOG_FILE = "access_log.json"

def get_logs():
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return []

def add_log(status):
    logs = get_logs()
    ip = f"192.168.1.{random.randint(10, 250)}"
    now = get_vn_time().strftime("%d/%m/%Y %H:%M:%S")
    logs.append({"time": now, "ip": ip, "status": status})
    with open(LOG_FILE, "w") as f:
        json.dump(logs[-5:], f)

# ==========================================
# QUẢN LÝ TRẠNG THÁI (SESSION STATE) & F5
# ==========================================
query_role = st.query_params.get("role", "")

if "system_auth" not in st.session_state:
    st.session_state.system_auth = (query_role in ["Admin", "Guest"])
if "logged_in" not in st.session_state:
    st.session_state.logged_in = (query_role in ["Admin", "Guest"])
if "role" not in st.session_state:
    st.session_state.role = query_role if query_role in ["Admin", "Guest"] else None

# ==========================================
# GIAO DIỆN CSS: CHIA 3 GIAI ĐOẠN ĐỘC LẬP
# ==========================================
css_code_login = """
    <style>
    .stApp { background-color: #2b4f35; background-image: radial-gradient(circle, #3a6845 10%, #1e3b28 80%); font-family: sans-serif; }
    [data-testid="stForm"] { background: #ffffff; padding: 40px 30px; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); border: none; }
    .stTextInput input { background-color: #ffffff !important; color: #333 !important; border: 1px solid #ccc !important; font-family: sans-serif !important; font-size: 14px !important; letter-spacing: normal; text-align: left; border-radius: 5px;}
    .stTextInput input:focus { border-color: #2b4f35 !important; box-shadow: 0 0 5px rgba(43,79,53,0.5) !important; }
    .stButton>button { background-color: #315b3a; color: #fff; border: none; border-radius: 5px; font-weight: bold; width: 100%; transition: 0.3s; margin-top: 15px; padding: 10px 0;}
    .stButton>button:hover { background-color: #1e3b28; color: #fff; }
    .log-table { width: 100%; border-collapse: collapse; margin-top: 30px; font-size: 12px; color: #eee; }
    .log-table th, .log-table td { border: 1px solid rgba(255,255,255,0.2); padding: 6px; text-align: center; }
    .log-table th { background-color: rgba(0,0,0,0.3); color: #fff; }
    .stat-ok { color: #4CAF50; font-weight: bold; }
    .stat-fail { color: #F44336; font-weight: bold; }
    .terminal-load { font-family: 'Consolas', monospace; color: #33ff33; font-size: 14px; line-height: 1.6; background: #000; padding: 20px; border-radius: 5px; border: 1px solid #33ff33; margin-top: 20px; text-align: left; }
    footer, #MainMenu, header {visibility: hidden;}
    </style>
"""

css_code_hacker = """
    <style>
    .stApp { background-color: #050505; color: #33ff33; font-family: 'Consolas', 'Courier New', monospace; }
    .login-box { max-width: 480px; margin: 40px auto; padding: 30px; background: #0f0f0f; border-radius: 10px; box-shadow: 0 5px 20px rgba(51, 255, 51, 0.25); text-align: center; border: 2px solid #33ff33;}
    .stTextInput input { background-color: #000 !important; color: #33ff33 !important; border: 1px solid #33ff33 !important; font-family: 'Consolas', monospace !important; font-size: 16px !important; letter-spacing: 2px; text-align: center;}
    .stButton>button { background-color: #0f0f0f; color: #33ff33; border: 1px solid #33ff33; font-family: 'Consolas', monospace; font-weight: bold; transition: 0.3s; width: 100%;}
    .stButton>button:hover { background-color: #33ff33; color: #000; box-shadow: 0 0 15px #33ff33; }
    footer, #MainMenu, header {visibility: hidden;}
    </style>
"""

css_code_work = """
    <style>
    .stApp { background-color: #F4F7F9; color: #31333F; font-family: sans-serif; }
    .codx-header { background: linear-gradient(135deg, #005B9F 0%, #0078D7 100%); padding: 15px 25px; border-radius: 8px; color: white; margin-bottom: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    .codx-title { font-size: 22px; font-weight: 700; margin: 0; }
    .codx-card { background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #EAECEF; }
    .stTextInput input { background-color: #ffffff !important; color: #000000 !important; border: 1px solid #cccccc !important; font-family: sans-serif !important; font-size: 14px !important; text-align: left;}
    .stTextInput input:focus { border-color: #0078D7 !important; box-shadow: 0 0 5px rgba(0,120,215,0.5) !important; }
    footer, #MainMenu, header {visibility: hidden;}
    
    /* Cấu hình ép bẻ dòng (Warp Text) cho bảng tĩnh HTML */
    .stTable { background-color: white; border-radius: 5px; overflow: hidden; margin-top: 10px; }
    .stTable table { width: 100% !important; border-collapse: collapse; }
    .stTable th, .stTable td { white-space: pre-wrap !important; word-wrap: break-word !important; border: 1px solid #e0e0e0; }
    .stTable th { background-color: #f8f9fa; font-weight: bold; }
    
    /* Chỉnh sửa thẩm mỹ cho Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #EAECEF; border-radius: 5px 5px 0 0; padding: 10px 20px; font-weight: bold;}
    .stTabs [aria-selected="true"] { background-color: #0078D7; color: white !important; }

    /* MEDIA QUERIES - TỐI ƯU GIAO DIỆN MOBILE & IPHONE 15 PRO MAX */
    @media screen and (max-width: 768px) {
        .codx-header { padding: 12px; text-align: center; }
        .codx-title { font-size: 18px !important; }
        .stTabs [data-baseweb="tab-list"] { overflow-x: auto; overflow-y: hidden; flex-wrap: nowrap; }
        .stTabs [data-baseweb="tab"] { padding: 8px 12px; font-size: 12px; white-space: nowrap; }
        .codx-card { padding: 10px; }
        .stMetric { text-align: center; }
        table { font-size: 11px !important; }
    }
    @media screen and (max-width: 430px) {
        .codx-title { font-size: 16px !important; }
        .stTabs [data-baseweb="tab"] { padding: 6px 10px; font-size: 11px; }
        .clock-container { font-size: 11px !important; padding: 4px 10px !important; }
        table th { font-size: 11px !important; padding: 2px !important; }
    }
    </style>
"""

if not st.session_state.system_auth:
    st.markdown(css_code_login, unsafe_allow_html=True)
elif not st.session_state.logged_in:
    st.markdown(css_code_hacker, unsafe_allow_html=True)
else:
    st.markdown(css_code_work, unsafe_allow_html=True)

# ==========================================
# GIAI ĐOẠN 1: MÀN HÌNH NHẬP MÃ BẢO MẬT
# ==========================================
if not st.session_state.system_auth:
    st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
    col_space1, col_left, col_space2, col_right, col_space3 = st.columns([0.5, 3.5, 0.5, 3.5, 0.5])
    
    with col_left:
        col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
        with col_logo2:
            if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        st.markdown("<h2 style='text-align:center; color:white; text-shadow: 1px 1px 5px rgba(0,0,0,0.5);'>HỆ THỐNG QUẢN TRỊ</h2>", unsafe_allow_html=True)
        
        logs = get_logs()
        if logs:
            st.markdown("<p style='text-align:center; color:#ddd; font-size:12px; margin-top:20px;'>[ LỊCH SỬ TRUY CẬP GẦN NHẤT ]</p>", unsafe_allow_html=True)
            html_table = '<table class="log-table"><tr><th>THỜI GIAN</th><th>IP TRUY CẬP</th><th>TRẠNG THÁI</th></tr>'
            for log in reversed(logs):
                css_class = "stat-ok" if log["status"] == "SUCCESS" else "stat-fail"
                html_table += f'<tr><td>{log["time"]}</td><td>{log["ip"]}</td><td class="{css_class}">{log["status"]}</td></tr>'
            html_table += '</table>'
            st.markdown(html_table, unsafe_allow_html=True)

    with col_right:
        st.markdown("<div style='height: 2vh;'></div>", unsafe_allow_html=True)
        with st.form("system_auth_form"):
            st.markdown("<h3 style='color:#333; text-align:center; margin-bottom:20px; font-weight:bold;'>ĐĂNG NHẬP</h3>", unsafe_allow_html=True)
            
            sys_user = st.text_input("👤 Tên tài khoản hoặc email", placeholder="Nhập tên tài khoản...")
            sys_pwd = st.text_input("🔒 Mật khẩu", type="password", placeholder="Nhập mật khẩu truy cập...")
            submit_auth = st.form_submit_button("ĐĂNG NHẬP")
            
            if submit_auth:
                if sys_user == "admin" and sys_pwd == "CY":
                    add_log("SUCCESS")
                    loader = st.empty()
                    base_txt = "> <span style='color:#00e5ff;'>Initializing secure protocol...</span> <span style='color:#00ff00;'>[OK]</span><br>> <span style='color:#ffcc00;'>Bypassing node security...</span> <span style='color:#00ff00;'>[OK]</span><br>> <b style='color:#ff3333;'>DECRYPTING MAINFRAME:</b><br><br>"
                    spinners = ['|', '/', '-', '\\']
                    
                    for i in range(1, 21):
                        bar_fill = "█" * i
                        bar_empty = "-" * (20 - i)
                        pct = i * 5
                        spin = spinners[i % 4]
                        html_load = f'<div class="terminal-load">{base_txt}<span style="color:#00ff00;">[{bar_fill}{bar_empty}] {pct}% {spin}</span></div>'
                        loader.markdown(html_load, unsafe_allow_html=True)
                        time.sleep(0.12)
                    
                    loader.markdown(f'<div class="terminal-load">{base_txt}<span style="color:#00ff00;">[████████████████████] 100%</span><br><br>> <span style="color:#00e5ff;">ACCESS GRANTED. PROCEED TO ROLE SELECTION.</span></div>', unsafe_allow_html=True)
                    time.sleep(0.8)
                    
                    st.session_state.system_auth = True
                    if 'df_master' in st.session_state:
                        del st.session_state['df_master']
                    loader.empty()
                    st.rerun()
                else:
                    add_log("FAILED")
                    st.error("🚨 TÀI KHOẢN HOẶC MẬT KHẨU KHÔNG CHÍNH XÁC. VUI LÒNG NHẬP LẠI!")
                    time.sleep(1)
                    st.rerun()
                    
    st.stop()

# ==========================================
# GIAI ĐOẠN 2: CHỌN QUYỀN ADMIN / GUEST 
# ==========================================
if st.session_state.system_auth and not st.session_state.logged_in:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    
    col_logo1, col_logo2, col_logo3 = st.columns([1, 1.5, 1])
    with col_logo2:
        if os.path.exists("logo.png"): st.image("logo.png", width=240)
            
    st.markdown("### 🛰️ CHỌN QUYỀN TRUY CẬP")
    st.markdown("<p style='color:#33ff33; opacity:0.7;'>Kết nối an toàn. Chọn chế độ tác chiến:</p>", unsafe_allow_html=True)
    
    if st.button("👁️ TRUY CẬP KHÁCH (CHỈ XEM)", use_container_width=True):
        st.session_state.role = "Guest"
        st.session_state.logged_in = True
        st.query_params["role"] = "Guest" 
        st.rerun()
        
    st.markdown("<hr style='border-color:#114411;'>", unsafe_allow_html=True)
    
    with st.form("admin_auth_form"):
        pwd = st.text_input("MẬT KHẨU ADMIN:", type="password")
        submit_admin = st.form_submit_button("🔓 ĐĂNG NHẬP NỘI BỘ (Enter)")
        if submit_admin:
            if pwd == "123":
                st.session_state.role = "Admin"
                st.session_state.logged_in = True
                st.query_params["role"] = "Admin" 
                st.rerun()
            else:
                st.error("🚨 Sai mật khẩu Admin!")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# GIAI ĐOẠN 3: ỨNG DỤNG LÀM VIỆC CHÍNH THỨC
# ==========================================
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1WNXCatSajRif42atvJ9B2tqG7gHlLkQVfXVN-FpUdi8/edit" 

conn = st.connection("gsheets", type=GSheetsConnection)
today = pd.Timestamp(get_vn_time().date())

# CẤU TRÚC LÕI ĐƯỢC ĐÓNG BĂNG BẢO VỆ 100%: KHÓA TRẠNG THÁI HOÀN THÀNH
def phan_loai(row):
    tt = str(row.get('TINH_TRANG', '')).strip()
    
    tt_norm = unicodedata.normalize('NFKD', tt.lower()).encode('ascii', 'ignore').decode('ascii')
    
    if "hoan thanh" in tt_norm or "xong" in tt_norm or "ok" in tt_norm or "🟢" in tt:
        return "🟢 Đã hoàn thành"
        
    if pd.isna(row.get('DEADLINE')) or row.get('DEADLINE') is pd.NaT or row.get('DEADLINE') is None:
        return tt if ("⏳" in tt or "🔴" in tt) else "⏳ Đang thực hiện"
        
    try:
        days_diff = (row['DEADLINE'] - today).days
        if days_diff < 0: return "🔴 Trễ hạn"
        if 0 <= days_diff <= 5: return "🔴 Cần thực hiện ngay"
    except:
        pass
        
    return "⏳ Đang thực hiện"

def get_col(df, keywords, fallback_idx):
    for col in df.columns:
        c_str = str(col).lower()
        c_norm = unicodedata.normalize('NFKD', c_str).encode('ascii', 'ignore').decode('ascii')
        for kw in keywords:
            if kw in c_str or kw in c_norm:
                return col
    if fallback_idx < len(df.columns): return df.columns[fallback_idx]
    return None

def style_status(val):
    val_str = str(val)
    if "Đã hoàn thành" in val_str:
        return 'background-color: #2e7d32; color: white;'
    elif "Cần thực hiện ngay" in val_str:
        return 'background-color: #d32f2f; color: white;'
    elif "Trễ hạn" in val_str:
        return 'background-color: #b71c1c; color: white;'
    return ''

def load_data():
    try:
        df_raw = conn.read(spreadsheet=SPREADSHEET_URL, ttl=0)
        
        cols_check = " ".join([str(c).lower() for c in df_raw.columns])
        if "tình trạng" in cols_check or "hạn chót" in cols_check or "deadline" in cols_check:
            df_raw.columns = [str(c).strip() for c in df_raw.columns]
        else:
            header_idx = -1
            for i, row in df_raw.head(10).iterrows():
                row_str = " ".join([str(val) for val in row]).lower()
                if ("hạn chót" in row_str or "deadline" in row_str) and ("tình trạng" in row_str or "trạng thái" in row_str):
                    header_idx = i
                    break
            
            if header_idx != -1:
                df_raw.columns = [str(c).strip() for c in df_raw.iloc[header_idx]]
                df_raw = df_raw.iloc[header_idx+1:].reset_index(drop=True)
            else:
                df_raw.columns = [str(c).strip() for c in df_raw.columns]

        extracted = {
            "TEN_BAO_CAO": df_raw["Tên công việc"] if "Tên công việc" in df_raw.columns else df_raw[get_col(df_raw, ["ten", "cong viec"], 1)],
            "KY_BAO_CAO": df_raw["Kỳ báo cáo"] if "Kỳ báo cáo" in df_raw.columns else df_raw[get_col(df_raw, ["ky", "thang", "quy"], 2)],
            "DEADLINE": df_raw["Hạn chót"] if "Hạn chót" in df_raw.columns else df_raw[get_col(df_raw, ["han", "deadline"], 3)],
            "TINH_TRANG": df_raw["Tình trạng"] if "Tình trạng" in df_raw.columns else df_raw[get_col(df_raw, ["tinh trang", "trang thai"], 4)],
            "DON_VI_YEU_CAU": df_raw["Đơn vị yêu cầu báo cáo"] if "Đơn vị yêu cầu báo cáo" in df_raw.columns else df_raw[get_col(df_raw, ["don vi", "yeu cau"], 5)],
            "LINH_VUC": df_raw["Lĩnh vực"] if "Lĩnh vực" in df_raw.columns else df_raw[get_col(df_raw, ["linh vuc"], 6)]
        }
        df = pd.DataFrame(extracted)
        
        df = df.dropna(subset=['TEN_BAO_CAO'])
        df['TEN_BAO_CAO'] = df['TEN_BAO_CAO'].astype(str)
        df['KY_BAO_CAO'] = df['KY_BAO_CAO'].astype(str).replace('nan', 'Không xác định')
        df['TINH_TRANG'] = df['TINH_TRANG'].astype(str).replace('nan', '⏳ Đang thực hiện')
        df['DON_VI_YEU_CAU'] = df['DON_VI_YEU_CAU'].astype(str).replace('nan', 'Không xác định')
        df['LINH_VUC'] = df['LINH_VUC'].astype(str).replace('nan', 'Không xác định')
        
        df['DEADLINE'] = pd.to_datetime(df['DEADLINE'], dayfirst=True, errors='coerce')
        df['TINH_TRANG'] = df.apply(phan_loai, axis=1)
        df['_ID'] = range(len(df))
        return df
    except Exception as e:
        st.error(f"❌ LỖI ĐỌC DỮ LIỆU: {e}")
        st.stop()

if "df_master" not in st.session_state:
    st.session_state.df_master = load_data()
if "editor_key" not in st.session_state:
    st.session_state.editor_key = str(uuid.uuid4())

# ------------------------------------------
# HEADER & BỘ CÔNG CỤ (TỐI ƯU MOBILE)
# ------------------------------------------
col_l, col_r = st.columns([1, 8])
with col_l:
    if os.path.exists("logo.png"): st.image("logo.png", width=90)

with col_r:
    r_txt = "Admin (Nội bộ)" if st.session_state.role == "Admin" else "Khách (Chỉ xem)"
    st.markdown(f"""
    <div class="codx-header">
        <p class="codx-title">☑️ HỆ THỐNG QUẢN TRỊ CÔNG VIỆC CAP AN KHÁNH</p>
        <p style="margin:0; opacity:0.9;">Quyền truy cập hiện tại: <b>{r_txt}</b></p>
    </div>
    """, unsafe_allow_html=True)

# Hiển thị vĩnh viễn 2 nút quan trọng ra ngoài cùng để Mobile luôn thấy
c_btn_top1, c_btn_top2 = st.columns(2)
with c_btn_top1:
    if st.button("🔄 LÀM MỚI DỮ LIỆU", use_container_width=True):
        st.cache_data.clear()
        st.session_state.df_master = load_data()
        st.session_state.editor_key = str(uuid.uuid4())
        st.rerun()
with c_btn_top2:
    if st.button("🚪 THOÁT / ĐĂNG XUẤT", type="primary", use_container_width=True):
        st.query_params.clear()
        st.session_state.clear()
        st.rerun()

# Thu gọn các công cụ Lọc vào Nút Expander để tiết kiệm diện tích dọc
with st.expander("🔽 BẤM VÀO ĐÂY ĐỂ MỞ / THU GỌN BỘ LỌC DỮ LIỆU", expanded=False):
    txt_search = st.text_input("🔍 Tìm Tên báo cáo:")
    
    k_list = st.session_state.df_master['KY_BAO_CAO'].unique().tolist()
    all_k = set([k for ky in k_list if isinstance(ky, str) for k in ky.split(", ")])
    
    ordered_periods = [
        "Tháng 01", "Tháng 02", "Tháng 03", "Quý 1", 
        "Tháng 04", "Tháng 05", "6 Tháng", "Tháng 06", 
        "Tháng 07", "Tháng 08", "Tháng 09", "Quý 3", 
        "Tháng 10", "Tháng 11", "Tháng 12", "Tổng kết năm"
    ]
    
    def sort_key(k):
        if k in ordered_periods:
            return (0, ordered_periods.index(k))
        return (1, k)
        
    sorted_all_k = sorted(list(all_k), key=sort_key)
    
    c_f1, c_f2 = st.columns(2)
    with c_f1:
        sel_ky = st.multiselect("Lọc Kỳ:", sorted_all_k, default=sorted_all_k)
        tt_opts = ["🔴 Trễ hạn", "🔴 Cần thực hiện ngay", "⏳ Đang thực hiện", "🟢 Đã hoàn thành"]
        sel_tt = st.multiselect("Lọc Tình trạng:", tt_opts, default=tt_opts)
    with c_f2:
        dv_opts = st.session_state.df_master['DON_VI_YEU_CAU'].unique().tolist()
        sel_dv = st.multiselect("Đơn vị yêu cầu:", dv_opts, default=dv_opts)
        lv_opts = st.session_state.df_master['LINH_VUC'].unique().tolist()
        sel_lv = st.multiselect("Lĩnh vực:", lv_opts, default=lv_opts)

def chk_ky(row_ky):
    if not sel_ky: return False
    return any(k in str(row_ky) for k in sel_ky)

mask = (
    st.session_state.df_master['TEN_BAO_CAO'].astype(str).str.contains(txt_search, case=False, na=False) &
    st.session_state.df_master['KY_BAO_CAO'].apply(chk_ky) &
    st.session_state.df_master['TINH_TRANG'].isin(sel_tt) &
    st.session_state.df_master['DON_VI_YEU_CAU'].isin(sel_dv) &
    st.session_state.df_master['LINH_VUC'].isin(sel_lv)
)
df_filtered = st.session_state.df_master[mask].copy()

# ==========================================
# CHUẨN BỊ BẢNG ĐỊNH DẠNG TĨNH (WRAP TEXT)
# ==========================================
df_display = df_filtered[["TEN_BAO_CAO", "KY_BAO_CAO", "DEADLINE", "TINH_TRANG", "DON_VI_YEU_CAU", "LINH_VUC"]].copy()
if pd.api.types.is_datetime64_any_dtype(df_display['DEADLINE']):
    df_display['DEADLINE'] = df_display['DEADLINE'].dt.strftime('%d/%m/%Y').fillna('')

df_display.columns = ["Tên công việc", "Kỳ báo cáo", "Hạn chót", "Tình trạng", "Đơn vị yêu cầu", "Lĩnh vực"]
styled_display = df_display.style.map(style_status, subset=['Tình trạng']).set_properties(
    subset=['Tên công việc'], **{'white-space': 'pre-wrap', 'min-width': '400px'}
)

# ------------------------------------------
# HIỂN THỊ BẢNG VÀ CHỨC NĂNG SẮP XẾP A-Z
# ------------------------------------------
metric_container = st.container()
st.markdown("<br>", unsafe_allow_html=True)
col_main, col_sub = st.columns([2.4, 1.0])

with col_main:
    st.markdown('<div class="codx-card">', unsafe_allow_html=True)
    st.subheader("📋 BẢNG CÔNG VIỆC CHI TIẾT")
    
    st.markdown("###### ↕️ LỌC VÀ SẮP XẾP (A-Z / Z-A) BỘ DỮ LIỆU GỐC")
    c_s1, c_s2 = st.columns([1.5, 2])
    
    sort_opts = [
        "Mặc định (Không sắp xếp)", "Tên công việc", "Kỳ báo cáo", 
        "Hạn chót", "Tình trạng", "Đơn vị yêu cầu báo cáo", "Lĩnh vực"
    ]
    with c_s1:
        sort_col = st.selectbox("Sắp xếp theo:", sort_opts)
    with c_s2:
        sort_asc = st.radio("Thứ tự:", ["A-Z (Tăng dần)", "Z-A (Giảm dần)"], horizontal=True)

    col_map = {
        "Tên công việc": "TEN_BAO_CAO", 
        "Kỳ báo cáo": "KY_BAO_CAO", 
        "Hạn chót": "DEADLINE", 
        "Tình trạng": "TINH_TRANG", 
        "Đơn vị yêu cầu báo cáo": "DON_VI_YEU_CAU",
        "Lĩnh vực": "LINH_VUC"
    }
    
    if sort_col != "Mặc định (Không sắp xếp)":
        is_asc = True if sort_asc == "A-Z (Tăng dần)" else False
        df_filtered = df_filtered.sort_values(
            by=col_map[sort_col], 
            ascending=is_asc, 
            na_position='last'
        )
    df_filtered = df_filtered.reset_index(drop=True)
    
    # CẤU TRÚC LÕI ĐƯỢC ĐÓNG BĂNG 100%: Xử lý định dạng ngày tháng để không lỗi sắp xếp tiêu đề
    df_interact = df_filtered.copy()
    df_interact['TEN_BAO_CAO'] = df_interact['TEN_BAO_CAO'].astype(str)
    df_interact['KY_BAO_CAO'] = df_interact['KY_BAO_CAO'].astype(str)
    df_interact['TINH_TRANG'] = df_interact['TINH_TRANG'].astype(str)
    df_interact['DON_VI_YEU_CAU'] = df_interact['DON_VI_YEU_CAU'].astype(str)
    df_interact['LINH_VUC'] = df_interact['LINH_VUC'].astype(str)
    df_interact['_ID'] = df_interact['_ID'].astype(int)
    
    df_interact['DEADLINE'] = pd.to_datetime(df_interact['DEADLINE'], errors='coerce')
    df_interact['DEADLINE'] = df_interact['DEADLINE'].where(df_interact['DEADLINE'].notnull(), None)

    tab_interact, tab_wrap = st.tabs(["📊 BẢNG TƯƠNG TÁC (Nhấn tiêu đề sắp xếp)", "📝 BẢNG CHI TIẾT (Tự động bẻ dòng Warp Text)"])
    
    with tab_interact:
        st.info("💡 **Gợi ý:** Bấm trực tiếp vào các thanh tiêu đề (Tên công việc, Hạn chót...) để sắp xếp tự động. **Nhấp đúp chuột vào ô Tên công việc** để xem toàn bộ nội dung và chỉnh sửa.")
        
        if st.session_state.role == "Admin":
            st.markdown("**KHU VỰC THAO TÁC (ADMIN):** Sửa trực tiếp, tick xoá, hoặc chọn hoàn thành.")
            df_interact.insert(0, "🗑️ Xóa", False)

            c_cols = {
                "_ID": None, 
                "🗑️ Xóa": st.column_config.CheckboxColumn("Xóa", default=False, width="small"),
                "TEN_BAO_CAO": st.column_config.TextColumn("Tên công việc", width="large"), 
                "KY_BAO_CAO": st.column_config.TextColumn("Kỳ báo cáo"), 
                "DEADLINE": st.column_config.DateColumn("Hạn chót", format="DD/MM/YYYY"),
                "TINH_TRANG": st.column_config.SelectboxColumn("Tình trạng", options=["🟢 Đã hoàn thành", "🔴 Cần thực hiện ngay", "🔴 Trễ hạn", "⏳ Đang thực hiện"], width="medium"),
                "DON_VI_YEU_CAU": st.column_config.TextColumn("Đơn vị yêu cầu", width="medium"),
                "LINH_VUC": st.column_config.TextColumn("Lĩnh vực", width="medium")
            }

            edited_df = st.data_editor(
                df_interact,
                key=st.session_state.editor_key,
                use_container_width=True, hide_index=True,
                column_config=c_cols
            )

            editor_state = st.session_state.get(st.session_state.editor_key, {})
            has_changes = False

            if editor_state.get("deleted_rows"):
                for idx in sorted(editor_state["deleted_rows"], reverse=True):
                    row_id = df_interact.iloc[idx]['_ID']
                    st.session_state.df_master = st.session_state.df_master[st.session_state.df_master['_ID'] != row_id]
                has_changes = True

            if editor_state.get("edited_rows"):
                for idx_str, changes in editor_state["edited_rows"].items():
                    idx = int(idx_str)
                    row_id = df_interact.iloc[idx]['_ID']
                    matching_indices = st.session_state.df_master.index[st.session_state.df_master['_ID'] == row_id].tolist()
                    if matching_indices:
                        m_idx = matching_indices[0]
                        if changes.get("🗑️ Xóa") == True:
                            st.session_state.df_master = st.session_state.df_master.drop(m_idx)
                        else:
                            for col, val in changes.items():
                                if col != "🗑️ Xóa":
                                    st.session_state.df_master.at[m_idx, col] = val
                            
                            if "TINH_TRANG" not in changes:
                                updated_row = st.session_state.df_master.loc[m_idx]
                                st.session_state.df_master.at[m_idx, 'TINH_TRANG'] = phan_loai(updated_row)
                has_changes = True

            if has_changes:
                st.session_state.editor_key = str(uuid.uuid4())
                st.rerun()

            if st.button("💾 LƯU ĐỒNG BỘ LÊN CLOUD", type="primary"):
                try:
                    df_to_save = st.session_state.df_master[["TEN_BAO_CAO", "KY_BAO_CAO", "DEADLINE", "TINH_TRANG", "DON_VI_YEU_CAU", "LINH_VUC"]].copy()
                    
                    df_to_save['DEADLINE'] = pd.to_datetime(df_to_save['DEADLINE']).dt.strftime('%d/%m/%Y').fillna('')
                    df_to_save.insert(0, "STT", range(1, len(df_to_save) + 1))
                    df_to_save.columns = ["STT", "Tên công việc", "Kỳ báo cáo", "Hạn chót", "Tình trạng", "Đơn vị yêu cầu báo cáo", "Lĩnh vực"]
                    
                    conn.update(worksheet="Data", data=df_to_save)
                    st.success("✅ Đã cập nhật thành công lên hệ thống gốc!")
                    
                    st.cache_data.clear()
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"🚨 LỖI LƯU CLOUD: {e}")
        else:
            g_cols = {
                "TEN_BAO_CAO": st.column_config.TextColumn("Tên công việc", width="large"), 
                "KY_BAO_CAO": st.column_config.TextColumn("Kỳ báo cáo"), 
                "DEADLINE": st.column_config.DateColumn("Hạn chót", format="DD/MM/YYYY"),
                "TINH_TRANG": st.column_config.TextColumn("Tình trạng", width="medium"),
                "DON_VI_YEU_CAU": st.column_config.TextColumn("Đơn vị yêu cầu", width="medium"),
                "LINH_VUC": st.column_config.TextColumn("Lĩnh vực", width="medium")
            }
            st.dataframe(
                df_interact[["TEN_BAO_CAO", "KY_BAO_CAO", "DEADLINE", "TINH_TRANG", "DON_VI_YEU_CAU", "LINH_VUC"]],
                use_container_width=True, hide_index=True, column_config=g_cols
            )

    with tab_wrap:
        st.info("👁️ **Chế độ xem bảng tĩnh:** Nội dung tự động bẻ dòng xuống hàng giống y hệt Excel để tiện việc theo dõi báo cáo dài, tuy nhiên bảng này không cho phép nhấn tiêu đề để sắp xếp.")
        st.table(styled_display)
        
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------
# BIỂU ĐỒ & LỊCH
# ------------------------------------------
with metric_container:
    c_m1, c_m2, c_m3 = st.columns(3)
    total = len(df_filtered)
    done = len(df_filtered[df_filtered['TINH_TRANG'] == "🟢 Đã hoàn thành"])
    late = len(df_filtered[df_filtered['TINH_TRANG'] == "🔴 Trễ hạn"])
    
    tl_ht = round(done/total*100) if total > 0 else 0
    
    with c_m1: st.metric("TỔNG CÔNG VIỆC", total)
    with c_m2: st.metric("ĐÃ XONG", done, f"{tl_ht}%")
    with c_m3: st.metric("TRỄ HẠN", late, delta_color="inverse", delta="Cảnh báo")

with col_sub:
    st.markdown('<div class="codx-card">', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-weight:bold;'>📊 TỶ LỆ TIẾN ĐỘ</p>", unsafe_allow_html=True)
    
    mau_bd = {"🟢 Đã hoàn thành": "#10B981", "🔴 Trễ hạn": "#EF4444", "⏳ Đang thực hiện": "#3B82F6", "🔴 Cần thực hiện ngay": "#F59E0B"}
    
    if total > 0:
        fig = px.pie(df_filtered, names='TINH_TRANG', hole=0.5, color='TINH_TRANG', color_discrete_map=mau_bd)
        fig.update_layout(showlegend=False, height=200, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div><br>', unsafe_allow_html=True)

    st.markdown('<div class="codx-card">', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-weight:bold;'>📅 LỊCH NHẮC VIỆC THÁNG NÀY</p>", unsafe_allow_html=True)
    
    html_clock = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body { margin: 0; padding: 0; display: flex; justify-content: center; font-family: sans-serif; background-color: white;}
        .clock-container { background:#EAECEF; padding: 5px 15px; border-radius:15px; font-size:13px; font-weight:bold; color:#005B9F; border: 1px solid #ccc; display: inline-block; margin-bottom: 12px; }
    </style>
    </head>
    <body>
        <div class="clock-container" id="vn-clock">🕒 Đang tải thời gian...</div>
        <script>
            function updateTime() {
                let d = new Date();
                let utc = d.getTime() + (d.getTimezoneOffset() * 60000);
                let nd = new Date(utc + (3600000*7)); // Múi giờ Việt Nam +7
                let day = String(nd.getDate()).padStart(2, '0');
                let month = String(nd.getMonth() + 1).padStart(2, '0');
                let year = nd.getFullYear();
                let hours = String(nd.getHours()).padStart(2, '0');
                let minutes = String(nd.getMinutes()).padStart(2, '0');
                let seconds = String(nd.getSeconds()).padStart(2, '0');
                document.getElementById("vn-clock").innerText = "🕒 " + day + "/" + month + "/" + year + " " + hours + ":" + minutes + ":" + seconds;
            }
            setInterval(updateTime, 1000);
            updateTime();
        </script>
    </body>
    </html>
    """
    components.html(html_clock, height=45)
    
    now_dt = get_vn_time()
    cal = calendar.monthcalendar(now_dt.year, now_dt.month)
    df_cx = df_filtered[df_filtered['TINH_TRANG'] != "🟢 Đã hoàn thành"].copy()
    
    df_cx_thang = df_cx[(df_cx['DEADLINE'].dt.month == now_dt.month) & (df_cx['DEADLINE'].dt.year == now_dt.year)]
    
    dls_urgent = df_cx_thang[(df_cx_thang['DEADLINE'] - today).dt.days <= 5]['DEADLINE'].dt.day.dropna().astype(int).unique().tolist()
    dls_all = df_cx_thang['DEADLINE'].dt.day.dropna().astype(int).unique().tolist()
    dls_normal = [d for d in dls_all if d not in dls_urgent]

    html_cal = '<table style="width:100%; border-collapse: collapse; font-size:13px; text-align:center;">'
    html_cal += '<tr><th style="color:#ff3333">CN</th><th>T2</th><th>T3</th><th>T4</th><th>T5</th><th>T6</th><th>T7</th></tr>'
    
    c_today_urgent = 'background:#EF4444; border: 3px solid #005B9F; color:white; border-radius:50%; width:28px; height:28px; line-height:22px; margin:auto; font-weight:bold; box-sizing:border-box; box-shadow: 0 0 8px rgba(0,91,159,0.5);'
    c_today = 'background:#0078D7; border: 3px solid #003366; color:white; border-radius:50%; width:28px; height:28px; line-height:22px; margin:auto; font-weight:bold; box-sizing:border-box; box-shadow: 0 0 8px rgba(0,120,215,0.7);'
    c_urgent = 'background:#EF4444; color:white; border-radius:50%; width:24px; height:24px; line-height:24px; margin:auto; font-weight:bold;'
    c_normal = 'background:#F59E0B; color:white; border-radius:50%; width:24px; height:24px; line-height:24px; margin:auto; font-weight:bold;'

    for week in cal:
        html_cal += '<tr>'
        for day in week:
            if day == 0: html_cal += '<td></td>'
            elif day == now_dt.day and day in dls_urgent: 
                html_cal += f'<td style="padding:5px;"><div style="{c_today_urgent}">{day}</div></td>'
            elif day == now_dt.day and day in dls_normal: 
                html_cal += f'<td style="padding:5px;"><div style="{c_today}">{day}</div></td>'
            elif day == now_dt.day: 
                html_cal += f'<td style="padding:5px;"><div style="{c_today}">{day}</div></td>'
            elif day in dls_urgent: 
                html_cal += f'<td style="padding:5px;"><div style="{c_urgent}">{day}</div></td>'
            elif day in dls_normal:
                html_cal += f'<td style="padding:5px;"><div style="{c_normal}">{day}</div></td>'
            else: html_cal += f'<td>{day}</td>'
        html_cal += '</tr>'
    html_cal += '</table>'
    st.markdown(html_cal, unsafe_allow_html=True)
    st.caption("🔴 Gấp/Trễ - 🟠 Còn hạn - 🔵 Viền xanh: Hôm nay")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 8. THÊM BÁO CÁO MỚI (CHỈ DÀNH CHO ADMIN)
# ==========================================
if st.session_state.role == "Admin":
    with col_main:
        st.markdown("<br>", unsafe_allow_html=True)
        k_map = {
            "Tháng 01": "2026-01-10", "Tháng 02": "2026-02-10", "Tháng 03": "2026-03-10", "Quý 1": "2026-03-10",
            "Tháng 04": "2026-04-10", "Tháng 05": "2026-05-10", "6 Tháng": "2026-06-10", "Tháng 06": "2026-06-10",
            "Tháng 07": "2026-07-10", "Tháng 08": "2026-08-10", "Tháng 09": "2026-09-10", "Quý 3": "2026-09-10",
            "Tháng 10": "2026-10-10", "Tháng 11": "2026-11-10", "Tháng 12": "2026-12-10", "Tổng kết năm": "2026-12-10"
        }

        with st.expander("➕ THÊM BÁO CÁO MỚI (Mở Form)"):
            with st.form("form_them", clear_on_submit=True):
                c_t1, c_t2, c_t3 = st.columns([2, 1, 1])
                with c_t1: f_ten = st.text_input("Tên báo cáo *")
                with c_t2: f_dv = st.text_input("Đơn vị yêu cầu")
                with c_t3: f_lv = st.text_input("Lĩnh vực")
                
                c_f1, c_f2, c_f3 = st.columns([2, 1, 1])
                with c_f1: 
                    f_k = st.multiselect("Kỳ báo cáo (Chọn từ danh sách)", options=list(k_map.keys()))
                    f_k_custom = st.text_input("Hoặc nhập kỳ báo cáo mới (nếu có)")
                    
                with c_f2: 
                    f_d = st.date_input("Hạn chót", value=get_vn_time().date())
                with c_f3: 
                    f_tt = st.selectbox("Tình trạng", ["⏳ Đang thực hiện", "🟢 Đã hoàn thành"])
                
                if st.form_submit_button("➕ Thêm vào danh sách (Nhấn Enter)"):
                    if f_ten:
                        new_data = []
                        max_id = st.session_state.df_master['_ID'].max() if not st.session_state.df_master.empty else -1
                        dv_val = f_dv.strip() if f_dv.strip() else "Không xác định"
                        lv_val = f_lv.strip() if f_lv.strip() else "Không xác định"

                        final_k = list(f_k)
                        if f_k_custom.strip():
                            final_k.append(f_k_custom.strip())

                        if final_k:
                            for k in final_k:
                                max_id += 1
                                m_date = k_map.get(k)
                                d_val = pd.to_datetime(m_date) if m_date else pd.to_datetime(f_d)
                                
                                new_data.append({
                                    "_ID": max_id, "TEN_BAO_CAO": f_ten, 
                                    "KY_BAO_CAO": k, "DEADLINE": d_val, 
                                    "TINH_TRANG": f_tt, "DON_VI_YEU_CAU": dv_val, "LINH_VUC": lv_val
                                })
                        else:
                            max_id += 1
                            new_data.append({
                                "_ID": max_id, "TEN_BAO_CAO": f_ten, 
                                "KY_BAO_CAO": "Không xác định", "DEADLINE": pd.to_datetime(f_d), 
                                "TINH_TRANG": f_tt, "DON_VI_YEU_CAU": dv_val, "LINH_VUC": lv_val
                            })

                        n_df = pd.DataFrame(new_data)
                        n_df['TINH_TRANG'] = n_df.apply(phan_loai, axis=1)
                        st.session_state.df_master = pd.concat(
                            [st.session_state.df_master, n_df], 
                            ignore_index=True
                        )
                        st.rerun()
