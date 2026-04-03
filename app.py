import streamlit as st
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
# GIAO DIỆN CSS: TÁCH BIỆT HACKER VÀ LÀM VIỆC
# ==========================================
if not st.session_state.logged_in:
    # ---------------- CSS HACKER (KHI CHƯA ĐĂNG NHẬP) ----------------
    css_code = """
        <style>
        .stApp { background-color: #050505; color: #33ff33; font-family: 'Consolas', 'Courier New', monospace; }
        .login-box { max-width: 480px; margin: 40px auto; padding: 30px; background: #0f0f0f; border-radius: 10px; box-shadow: 0 5px 20px rgba(51, 255, 51, 0.25); text-align: center; border: 2px solid #33ff33;}
        .log-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 12px; color: #33ff33; }
        .log-table th, .log-table td { border: 1px solid #114411; padding: 6px; text-align: center; }
        .log-table th { background-color: #002200; color: #55ff55; }
        .stat-ok { color: #00ff00; font-weight: bold; }
        .stat-fail { color: #ff3333; font-weight: bold; }
        .stTextInput input { background-color: #000 !important; color: #33ff33 !important; border: 1px solid #33ff33 !important; font-family: 'Consolas', monospace !important; font-size: 16px !important; letter-spacing: 2px; text-align: center;}
        .stButton>button { background-color: #0f0f0f; color: #33ff33; border: 1px solid #33ff33; font-family: 'Consolas', monospace; font-weight: bold; transition: 0.3s; width: 100%;}
        .stButton>button:hover { background-color: #33ff33; color: #000; box-shadow: 0 0 15px #33ff33; }
        .terminal-load { font-family: 'Consolas', monospace; color: #33ff33; font-size: 15px; line-height: 1.6; background: #000; padding: 20px; border-radius: 5px; border: 1px solid #33ff33; margin-bottom: 20px; text-align: left; }
        footer, #MainMenu, header {visibility: hidden;}
        </style>
    """
else:
    # ---------------- CSS HIỆN ĐẠI (KHI ĐÃ ĐĂNG NHẬP VÀO LÀM VIỆC) ----------------
    css_code = """
        <style>
        .stApp { background-color: #F4F7F9; color: #31333F; font-family: sans-serif; }
        .codx-header { background: linear-gradient(135deg, #005B9F 0%, #0078D7 100%); padding: 15px 25px; border-radius: 8px; color: white; margin-bottom: 25px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .codx-title { font-size: 22px; font-weight: 700; margin: 0; }
        .codx-card { background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #EAECEF; }
        .stTextInput input { background-color: #ffffff !important; color: #000000 !important; border: 1px solid #cccccc !important; font-family: sans-serif !important; font-size: 14px !important; letter-spacing: 0px; text-align: left;}
        .stTextInput input:focus { border-color: #0078D7 !important; box-shadow: 0 0 5px rgba(0,120,215,0.5) !important; }
        footer, #MainMenu, header {visibility: hidden;}
        </style>
    """
st.markdown(css_code, unsafe_allow_html=True)

# ==========================================
# GIAI ĐOẠN 1: MÀN HÌNH NHẬP MÃ BẢO MẬT "CY"
# ==========================================
if not st.session_state.system_auth:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    
    col_logo1, col_logo2, col_logo3 = st.columns([1, 1.5, 1])
    with col_logo2:
        if os.path.exists("logo.png"): st.image("logo.png", width=240)
            
    st.markdown("### 🖥️ HỆ THỐNG GIÁM SÁT AN NINH MẠNG")
    
    st.markdown("<div style='text-align:left; font-size:13px; margin-bottom:5px;'>[ 5 LỊCH SỬ TRUY CẬP GẦN NHẤT ]:</div>", unsafe_allow_html=True)
    logs = get_logs()
    if not logs:
        st.markdown("<p style='color:#88ff88; font-size:13px;'>Chưa có dữ liệu truy cập.</p>", unsafe_allow_html=True)
    else:
        html_table = '<table class="log-table"><tr><th>THỜI GIAN</th><th>IP TRUY CẬP</th><th>TRẠNG THÁI</th></tr>'
        for log in reversed(logs):
            css_class = "stat-ok" if log["status"] == "SUCCESS" else "stat-fail"
            html_table += f'<tr><td>{log["time"]}</td><td>{log["ip"]}</td><td class="{css_class}">{log["status"]}</td></tr>'
        html_table += '</table>'
        st.markdown(html_table, unsafe_allow_html=True)
        
    st.markdown("<p style='color:#33ff33; opacity:0.7;'>Vui lòng nhập mã đăng nhập để truy cập</p>", unsafe_allow_html=True)
    
    with st.form("system_auth_form"):
        sys_pwd = st.text_input("MÃ ĐĂNG NHẬP:", type="password")
        submit_auth = st.form_submit_button("XÁC THỰC KẾT NỐI (Enter)")
        
        if submit_auth:
            if sys_pwd == "CY":
                add_log("SUCCESS")
                
                # HIỆU ỨNG LOADING CHẠY NGANG - MÀU MÈ, CHUYÊN NGHIỆP HƠN
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
                    time.sleep(0.15)
                
                loader.markdown(f'<div class="terminal-load">{base_txt}<span style="color:#00ff00;">[████████████████████] 100%</span><br><br>> <span style="color:#00e5ff;">ACCESS GRANTED. PROCEED TO ROLE SELECTION.</span></div>', unsafe_allow_html=True)
                time.sleep(0.8)
                
                st.session_state.system_auth = True
                loader.empty()
                st.rerun()
            else:
                add_log("FAILED")
                st.error("🚨 MÃ ĐĂNG NHẬP KHÔNG CHÍNH XÁC!")
                time.sleep(1)
                st.rerun()
                
    st.markdown('</div>', unsafe_allow_html=True)
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
        # Đọc dữ liệu từ Gsheets
        df_raw = conn.read(spreadsheet=SPREADSHEET_URL)
        
        # Cắt lấy 6 cột
        if len(df_raw.columns) >= 7:
            df = df_raw.iloc[:, 1:7].copy()
        else:
            df = df_raw.copy()
            
        while len(df.columns) < 6:
            df[f"Cot_{len(df.columns)}"] = ""
            
        df.columns = ["TEN_BAO_CAO", "KY_BAO_CAO", "DEADLINE", "TRANG_THAI_GOC", "DON_VI_YEU_CAU", "LINH_VUC"]
        df = df.dropna(subset=['TEN_BAO_CAO'])
        
        # CHỐNG LỖI ATTRIBUTE ERROR (.str.contains) => Ép kiểu toàn bộ về string
        df['TEN_BAO_CAO'] = df['TEN_BAO_CAO'].astype(str)
        df['KY_BAO_CAO'] = df['KY_BAO_CAO'].astype(str).replace('nan', 'Không xác định')
        df['TRANG_THAI_GOC'] = df['TRANG_THAI_GOC'].astype(str).replace('nan', 'Chưa xử lý')
        df['DON_VI_YEU_CAU'] = df['DON_VI_YEU_CAU'].astype(str).replace('nan', 'Không xác định')
        df['LINH_VUC'] = df['LINH_VUC'].astype(str).replace('nan', 'Không xác định')
        
        df['DEADLINE'] = pd.to_datetime(df['DEADLINE'], errors='coerce')
        df['THANG'] = df['DEADLINE'].dt.month.fillna(0).astype(int)
        
        df['CANH_BAO'] = df.apply(phan_loai, axis=1)
        df['_ID'] = range(len(df))
        return df
    except Exception as e:
        st.error(f"❌ LỖI ĐỌC GOOGLE SHEETS: {e}")
        st.stop()

if "df_master" not in st.session_state:
    st.session_state.df_master = load_data()
if "editor_key" not in st.session_state:
    st.session_state.editor_key = str(uuid.uuid4())

# ------------------------------------------
# HEADER & BỘ LỌC
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

if st.sidebar.button("🚪 THOÁT / ĐĂNG XUẤT", type="primary"):
    st.query_params.clear()
    st.session_state.clear()
    st.rerun()

with st.sidebar:
    st.header("🔍 BỘ LỌC TÌM KIẾM")
    txt_search = st.text_input("Tên báo cáo:")
    
    k_list = st.session_state.df_master['KY_BAO_CAO'].unique().tolist()
    all_k = set([k for ky in k_list if isinstance(ky, str) for k in ky.split(", ")])
    sel_ky = st.multiselect("Lọc Kỳ:", list(all_k), default=list(all_k))
    
    t_list = sorted([m for m in st.session_state.df_master['THANG'].unique() if m != 0])
    t_opts = t_list + [0]
    
    def fmt_m(x): return f"Tháng {x}" if x != 0 else "Chưa có hạn"
    sel_thang = st.multiselect("Lọc Tháng:", options=t_opts, default=t_opts, format_func=fmt_m)
    
    tt_opts = ["🚨 TRỄ HẠN", "🔥 CẦN LÀM GẤP", "⏳ ĐANG THỰC HIỆN", "✅ HOÀN THÀNH"]
    sel_tt = st.multiselect("Trạng thái:", tt_opts, default=tt_opts)

    dv_opts = st.session_state.df_master['DON_VI_YEU_CAU'].unique().tolist()
    sel_dv = st.multiselect("Đơn vị yêu cầu:", dv_opts, default=dv_opts)
    
    lv_opts = st.session_state.df_master['LINH_VUC'].unique().tolist()
    sel_lv = st.multiselect("Lĩnh vực:", lv_opts, default=lv_opts)
    
    st.divider()
    if st.button("🔄 Làm mới dữ liệu", use_container_width=True):
        st.cache_data.clear()
        st.session_state.df_master = load_data() 
        st.rerun()

def chk_ky(row_ky):
    if not sel_ky: return False
    return any(k in str(row_ky) for k in sel_ky)

# Ép kiểu str() cho cột TEN_BAO_CAO lúc quét mask để chống lỗi 100%
mask = (
    st.session_state.df_master['TEN_BAO_CAO'].astype(str).str.contains(txt_search, case=False, na=False) &
    st.session_state.df_master['KY_BAO_CAO'].apply(chk_ky) &
    st.session_state.df_master['THANG'].isin(sel_thang) &
    st.session_state.df_master['CANH_BAO'].isin(sel_tt) &
    st.session_state.df_master['DON_VI_YEU_CAU'].isin(sel_dv) &
    st.session_state.df_master['LINH_VUC'].isin(sel_lv)
)
df_filtered = st.session_state.df_master[mask].copy()

# ------------------------------------------
# HIỂN THỊ BẢNG VÀ CHỨC NĂNG SẮP XẾP A-Z
# ------------------------------------------
metric_container = st.container()
st.markdown("<br>", unsafe_allow_html=True)
col_main, col_sub = st.columns([2.4, 1.0])

with col_main:
    st.markdown('<div class="codx-card">', unsafe_allow_html=True)
    st.subheader("📋 BẢNG CÔNG VIỆC CHI TIẾT")
    
    # --- BỘ CÔNG CỤ SẮP XẾP A-Z ---
    st.markdown("###### ↕️ LỌC VÀ SẮP XẾP (A-Z / Z-A)")
    c_s1, c_s2 = st.columns([1.5, 2])
    
    sort_opts = [
        "Mặc định (Không sắp xếp)", "Tên công việc", "Kỳ báo cáo", 
        "Hạn chót", "Trạng thái gốc", "Đơn vị yêu cầu báo cáo", "Lĩnh vực"
    ]
    with c_s1:
        sort_col = st.selectbox("Sắp xếp theo:", sort_opts)
    with c_s2:
        sort_asc = st.radio("Thứ tự:", ["A-Z (Tăng dần)", "Z-A (Giảm dần)"], horizontal=True)

    col_map = {
        "Tên công việc": "TEN_BAO_CAO", 
        "Kỳ báo cáo": "KY_BAO_CAO", 
        "Hạn chót": "DEADLINE", 
        "Trạng thái gốc": "TRANG_THAI_GOC", 
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
    
    # --- HIỂN THỊ DỮ LIỆU ---
    if st.session_state.role == "Admin":
        st.info("💡 Bấm trực tiếp vào bảng để Sửa/Xóa. Sau đó bấm **LƯU ĐỒNG BỘ LÊN CLOUD**.")
        df_filtered.insert(0, "🗑️ Xóa", False)

        c_cols = {
            "_ID": None, 
            "🗑️ Xóa": st.column_config.CheckboxColumn("Xóa", default=False, width="small"),
            "TEN_BAO_CAO": st.column_config.TextColumn("Tên công việc", width="large"), 
            "KY_BAO_CAO": st.column_config.TextColumn("Kỳ báo cáo"), 
            "DEADLINE": st.column_config.DateColumn("Hạn chót", format="DD/MM/YYYY"),
            "TRANG_THAI_GOC": st.column_config.SelectboxColumn("Trạng thái", options=["Chưa xử lý", "Đang thực hiện", "Hoàn thành"]),
            "CANH_BAO": st.column_config.TextColumn("Tình trạng", disabled=True),
            "DON_VI_YEU_CAU": st.column_config.TextColumn("Đơn vị yêu cầu", width="medium"),
            "LINH_VUC": st.column_config.TextColumn("Lĩnh vực", width="medium")
        }

        edited_df = st.data_editor(
            df_filtered,
            key=st.session_state.editor_key,
            use_container_width=True, hide_index=True, num_rows="dynamic",
            column_config=c_cols
        )

        del_ids = edited_df[edited_df["🗑️ Xóa"] == True]["_ID"].tolist()
        if del_ids:
            st.session_state.df_master = st.session_state.df_master[~st.session_state.df_master["_ID"].isin(del_ids)]
            st.rerun() 
            
        edited_df = edited_df[edited_df["🗑️ Xóa"] == False]
        for _, row in edited_df.iterrows():
            m_idx = st.session_state.df_master.index[st.session_state.df_master['_ID'] == row['_ID']].tolist()[0]
            st.session_state.df_master.at[m_idx, 'TEN_BAO_CAO'] = row['TEN_BAO_CAO']
            st.session_state.df_master.at[m_idx, 'KY_BAO_CAO'] = row['KY_BAO_CAO']
            st.session_state.df_master.at[m_idx, 'DEADLINE'] = row['DEADLINE']
            st.session_state.df_master.at[m_idx, 'TRANG_THAI_GOC'] = row['TRANG_THAI_GOC']
            st.session_state.df_master.at[m_idx, 'DON_VI_YEU_CAU'] = row['DON_VI_YEU_CAU']
            st.session_state.df_master.at[m_idx, 'LINH_VUC'] = row['LINH_VUC']
            st.session_state.df_master.at[m_idx, 'CANH_BAO'] = phan_loai(row)

        if st.button("💾 LƯU ĐỒNG BỘ LÊN CLOUD", type="primary"):
            try:
                df_to_save = st.session_state.df_master[["TEN_BAO_CAO", "KY_BAO_CAO", "DEADLINE", "TRANG_THAI_GOC", "DON_VI_YEU_CAU", "LINH_VUC"]].copy()
                df_to_save.insert(0, "STT_ID", range(1, len(df_to_save) + 1))
                conn.update(worksheet="Data", data=df_to_save)
                st.success("✅ Đã cập nhật thành công lên hệ thống gốc!")
                st.cache_data.clear()
                st.session_state.df_master = load_data()
                st.rerun()
            except Exception as e:
                st.error(f"🚨 LỖI LƯU CLOUD: {e}")
    else:
        st.info("👁️ **CHẾ ĐỘ XEM:** Đang xem với quyền Khách (Read-only).")
        st.dataframe(
            df_filtered[["TEN_BAO_CAO", "KY_BAO_CAO", "DEADLINE", "TRANG_THAI_GOC", "CANH_BAO", "DON_VI_YEU_CAU", "LINH_VUC"]],
            use_container_width=True, hide_index=True,
            column_config={
                "DEADLINE": st.column_config.DateColumn("Hạn chót", format="DD/MM/YYYY")
            }
        )
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------
# BIỂU ĐỒ & LỊCH
# ------------------------------------------
with metric_container:
    c_m1, c_m2, c_m3 = st.columns(3)
    total = len(df_filtered)
    done = len(df_filtered[df_filtered['CANH_BAO'] == "✅ HOÀN THÀNH"])
    late = len(df_filtered[df_filtered['CANH_BAO'] == "🚨 TRỄ HẠN"])
    
    tl_ht = round(done/total*100) if total > 0 else 0
    
    with c_m1: st.metric("TỔNG CÔNG VIỆC", total)
    with c_m2: st.metric("ĐÃ XONG", done, f"{tl_ht}%")
    with c_m3: st.metric("TRỄ HẠN", late, delta_color="inverse", delta="Cảnh báo")

with col_sub:
    st.markdown('<div class="codx-card">', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-weight:bold;'>📊 TỶ LỆ TIẾN ĐỘ</p>", unsafe_allow_html=True)
    
    mau_bd = {"✅ HOÀN THÀNH": "#10B981", "🚨 TRỄ HẠN": "#EF4444", "⏳ ĐANG THỰC HIỆN": "#3B82F6", "🔥 CẦN LÀM GẤP": "#F59E0B"}
    
    if total > 0:
        fig = px.pie(df_filtered, names='CANH_BAO', hole=0.5, color='CANH_BAO', color_discrete_map=mau_bd)
        fig.update_layout(showlegend=False, height=200, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div><br>', unsafe_allow_html=True)

    st.markdown('<div class="codx-card">', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-weight:bold;'>📅 LỊCH NHẮC VIỆC THÁNG</p>", unsafe_allow_html=True)
    
    now = datetime.datetime.now()
    cal = calendar.monthcalendar(now.year, now.month)
    df_cx = df_filtered[df_filtered['CANH_BAO'] != "✅ HOÀN THÀNH"].copy()
    df_cx_thang = df_cx[df_cx['DEADLINE'].dt.month == now.month]
    dls = df_cx_thang['DEADLINE'].dt.day.dropna().astype(int).unique().tolist()

    html_cal = '<table style="width:100%; border-collapse: collapse; font-size:13px; text-align:center;">'
    html_cal += '<tr><th style="color:#ff3333">CN</th><th>T2</th><th>T3</th><th>T4</th><th>T5</th><th>T6</th><th>T7</th></tr>'
    
    for week in cal:
        html_cal += '<tr>'
        for day in week:
            if day == 0: html_cal += '<td></td>'
            elif day == now.day: html_cal += f'<td style="background-color:#0078D7; border-radius:50%; font-weight:bold; color:#fff;">{day}</td>'
            elif day in dls: html_cal += f'<td style="background-color:#EF4444; border-radius:50%; font-weight:bold; color:#fff;">{day}</td>'
            else: html_cal += f'<td>{day}</td>'
        html_cal += '</tr>'
    html_cal += '</table>'
    st.markdown(html_cal, unsafe_allow_html=True)
    st.caption("🔴 Đỏ: Hạn nộp - 🔵 Xanh: Hôm nay")
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
                    f_k = st.multiselect("Kỳ báo cáo", options=list(k_map.keys()))
                with c_f2: 
                    f_d = st.date_input("Hạn chót", value=datetime.date.today())
                with c_f3: 
                    f_tt = st.selectbox("Trạng thái", ["Chưa xử lý", "Đang thực hiện", "Hoàn thành"])
                
                if st.form_submit_button("➕ Thêm vào danh sách (Nhấn Enter)"):
                    if f_ten:
                        new_data = []
                        max_id = st.session_state.df_master['_ID'].max() if not st.session_state.df_master.empty else -1
                        dv_val = f_dv.strip() if f_dv.strip() else "Không xác định"
                        lv_val = f_lv.strip() if f_lv.strip() else "Không xác định"

                        if f_k:
                            for k in f_k:
                                max_id += 1
                                m_date = k_map.get(k)
                                d_val = pd.to_datetime(m_date) if m_date else pd.to_datetime(f_d)
                                
                                new_data.append({
                                    "_ID": max_id, "TEN_BAO_CAO": f_ten, 
                                    "KY_BAO_CAO": k, "DEADLINE": d_val, 
                                    "TRANG_THAI_GOC": f_tt, "DON_VI_YEU_CAU": dv_val, "LINH_VUC": lv_val
                                })
                        else:
                            max_id += 1
                            new_data.append({
                                "_ID": max_id, "TEN_BAO_CAO": f_ten, 
                                "KY_BAO_CAO": "Không xác định", "DEADLINE": pd.to_datetime(f_d), 
                                "TRANG_THAI_GOC": f_tt, "DON_VI_YEU_CAU": dv_val, "LINH_VUC": lv_val
                            })

                        n_df = pd.DataFrame(new_data)
                        n_df['THANG'] = n_df['DEADLINE'].dt.month.fillna(0).astype(int)
                        n_df['CANH_BAO'] = n_df.apply(phan_loai, axis=1)
                        st.session_state.df_master = pd.concat(
                            [st.session_state.df_master, n_df], 
                            ignore_index=True
                        )
                        st.rerun()
