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
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
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
    .codx-header { background: linear-gradient(135deg, #005B9F 0%, #0078D7 100%); padding: 15px 25px; border-radius: 8px; color: white; margin-bottom: 25px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
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
today = pd.Timestamp.today().normalize()

# KHẮC PHỤC LỖI 2: KHÓA CỨNG TRẠNG THÁI HOÀN THÀNH
def phan_loai(row):
    tt = str(row.get('TINH_TRANG', '')).strip().lower()
    tt_norm = unicodedata.normalize('NFKD', tt).encode('ascii', 'ignore').decode('ascii')
    
    # 1. Cứ thấy dấu hiệu hoàn thành/xong là lập tức trả về xanh, bỏ qua check ngày!
    if "hoan" in tt_norm or "xong" in tt_norm or "ok" in tt_norm or "🟢" in tt:
        return "🟢 Đã hoàn thành"
        
    # 2. Xử lý các tình huống còn lại
    if pd.isna(row.get('DEADLINE')) or row.get('DEADLINE') is pd.NaT:
        return "⏳ Đang thực hiện"
        
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
        if any(kw in c_str or kw in c_norm for kw in keywords):
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
        
        header_idx = -1
        for i, row in df_raw.head(10).iterrows():
            row_str = " ".join([str(val) for val in row]).lower()
            if "báo cáo" in row_str or "hạn chót" in row_str or "tình trạng" in row_str or "trạng thái" in row_str:
                header_idx = i
                break
        
        if header_idx != -1:
            df_raw.columns = [str(c).strip() for c in df_raw.iloc[header_idx]]
            df_raw = df_raw.iloc[header_idx+1:].reset_index(drop=True)
        else:
            df_raw.columns = [str(c).strip() for c in df_raw.columns]

        col_ten = get_col(df_raw, ["ten", "cong viec", "công", "báo cáo"], 1)
        col_ky = get_col(df_raw, ["ky", "kỳ"], 2)
        col_han = get_col(df_raw, ["han", "deadline", "chót", "chot"], 3)
        col_tt = get_col(df_raw, ["tinh trang", "trang thai", "tt", "trạng"], 4)
        col_dv = get_col(df_raw, ["don vi", "yeu cau", "đơn"], 5)
        col_lv = get_col(df_raw, ["linh vuc", "lĩnh", "vuc"], 6)

        extracted = {
            "TEN_BAO_CAO": df_raw[col_ten] if col_ten else pd.Series([""]*len(df_raw)),
            "KY_BAO_CAO": df_raw[col_ky] if col_ky else pd.Series([""]*len(df_raw)),
            "DEADLINE": df_raw[col_han] if col_han else pd.Series([""]*len(df_raw)),
            "TINH_TRANG": df_raw[col_tt] if col_tt else pd.Series([""]*len(df_raw)),
            "DON_VI_YEU_CAU": df_raw[col_dv] if col_dv else pd.Series([""]*len(df_raw)),
            "LINH_VUC": df_raw[col_lv] if col_lv else pd.Series([""]*len(df_raw))
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
