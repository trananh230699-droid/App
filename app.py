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
    page_title="Hệ thống Quản trị - CA An Khánh", 
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
    # Giả lập IP ảo cho ngầu hoặc lấy IP nội bộ
    ip = f"192.168.1.{random.randint(10, 250)}"
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    logs.append({"time": now, "ip": ip, "status": status})
    with open(LOG_FILE, "w") as f:
        json.dump(logs[-50:], f) # Lưu tối đa 50 lượt gần nhất

# ==========================================
# 1. ĐỌC PHIÊN ĐĂNG NHẬP (CHỐNG F5)
# ==========================================
# Lấy quyền từ trình duyệt (giúp F5 không bị mất)
current_role = st.query_params.get("role", None)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = (current_role is not None)
if "role" not in st.session_state:
    st.session_state.role = current_role

# ==========================================
# 2. MÀN HÌNH TERMINAL HACKER (KHI CHƯA ĐĂNG NHẬP)
# ==========================================
if not st.session_state.logged_in:
    # CSS ĐỘC QUYỀN CHO MÀN HÌNH TERMINAL
    st.markdown("""
        <style>
        .stApp { background-color: #080c08; color: #33ff33; font-family: 'Courier New', Courier, monospace; }
        .term-box { background-color: rgba(0, 20, 0, 0.85); border: 1px solid #00ff00; border-radius: 10px; padding: 30px; max-width: 750px; margin: 40px auto; box-shadow: 0 0 25px rgba(0, 255, 0, 0.15); }
        .term-header { text-align: center; border-bottom: 1px dashed #33ff33; padding-bottom: 15px; margin-bottom: 20px; }
        .term-title { font-size: 22px; font-weight: bold; margin: 10px 0 5px 0; text-shadow: 0 0 5px #33ff33; }
        .term-subtitle { font-size: 14px; color: #88ff88; }
        
        /* Bảng lịch sử */
        .log-table { width: 100%; border-collapse: collapse; margin-bottom: 25px; font-size: 13px; }
        .log-table th, .log-table td { border: 1px solid #114411; padding: 8px; text-align: left; }
        .log-table th { background-color: #002200; color: #55ff55; }
        .stat-ok { color: #00ff00; font-weight: bold; }
        .stat-fail { color: #ff3333; font-weight: bold; }
        
        /* Ô nhập Pass & Nút bấm */
        .stTextInput input { background-color: #001100 !important; color: #33ff33 !important; border: 1px solid #33ff33 !important; font-family: 'Courier New', monospace !important; text-align: center; font-size: 20px !important; letter-spacing: 4px; border-radius: 5px; }
        .stTextInput input:focus { box-shadow: 0 0 10px #33ff33 !important; }
        .stButton>button { background-color: #002200; color: #33ff33; border: 1px solid #33ff33; width: 100%; font-family: 'Courier New', monospace; font-weight: bold; font-size: 16px; transition: 0.3s; border-radius: 5px;}
        .stButton>button:hover { background-color: #33ff33; color: #000000; box-shadow: 0 0 15px #33ff33; }
        </style>
    """, unsafe_allow_html=True)

    # Vùng chứa Terminal
    st.markdown('<div class="term-box">', unsafe_allow_html=True)
    
    # 1. Phần Logo tinh tế ở giữa
    c_logo1, c_logo2, c_logo3 = st.columns([1, 1, 1])
    with c_logo2:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
            
    # 2. Tiêu đề
    st.markdown("""
        <div class="term-header">
            <div class="term-title">[ SECURITY KERNEL ] - C.A.P AN KHÁNH</div>
            <div class="term-subtitle">FULL ACCESS MONITORING SYSTEM V2.0</div>
        </div>
    """, unsafe_allow_html=True)

    # 3. Bảng hiển thị 5 lịch sử gần nhất
    st.markdown("`[ LỊCH SỬ TRUY CẬP HỆ THỐNG GẦN NHẤT ]`")
    logs = get_logs()[-5:] # Lấy 5 dòng cuối
    if not logs:
        st.markdown("<p style='color:#88ff88; font-size:13px;'>Chưa có dữ liệu truy cập.</p>", unsafe_allow_html=True)
    else:
        html_table = '<table class="log-table"><tr><th>THỜI GIAN</th><th>IP TRUY CẬP</th><th>KẾT QUẢ</th></tr>'
        for log in reversed(logs): # Đảo ngược để cái mới nhất lên đầu
            css_class = "stat-ok" if log["status"] == "SUCCESS" else "stat-fail"
            html_table += f'<tr><td>{log["time"]}</td><td>{log["ip"]}</td><td class="{css_class}">{log["status"]}</td></tr>'
        html_table += '</table>'
        st.markdown(html_table, unsafe_allow_html=True)

    # 4. Khu vực nhập mật khẩu (Form để bấm Enter)
    term_placeholder = st.empty()
    
    with term_placeholder.form("terminal_login"):
        pwd = st.text_input("VUI LÒNG NHẬP MẬT KHẨU QUẢN TRỊ (Hoặc bỏ trống để vào ẩn danh):", type="password")
        col_btn1, col_btn2 = st.columns([2, 1])
        with col_btn1:
            submit_auth = st.form_submit_button("🔓 XÁC NHẬN (Nhấn Enter)")
        with col_btn2:
            submit_guest = st.form_submit_button("👁️ TRUY CẬP KHÁCH")
        
        if submit_auth or submit_guest:
            # Xử lý Logic
            if submit_guest or (submit_auth and pwd == ""):
                selected_role = "Guest"
                add_log("SUCCESS")
            elif submit_auth and pwd == "123":
                selected_role = "Admin"
                add_log("SUCCESS")
            else:
                selected_role = None
                add_log("FAILED")
                
            # Đăng nhập thành công -> Chạy hiệu ứng Loading Hacker
            if selected_role:
                term_placeholder.empty() # Xóa form nhập pass
                loading_box = st.empty()
                
                # Hiệu ứng gõ chữ
                loading_text = "> VERIFYING CREDENTIALS... [ OK ]\n"
                loading_box.markdown(f"```text\n{loading_text}```")
                time.sleep(0.4)
                
                loading_text += "> ESTABLISHING SECURE CONNECTION... [ OK ]\n> DECRYPTING MAINFRAME:\n"
                
                # Chạy thanh tiến trình mượt mà
                for i in range(1, 21):
                    bar = "█" * i + "-" * (20 - i)
                    pct = i * 5
                    loading_box.markdown(f"```text\n{loading_text}  [{bar}] {pct}%\n```")
                    time.sleep(0.05)
                
                loading_box.markdown(f"```text\n{loading_text}  [████████████████████] 100%\n> ACCESS GRANTED. INITIALIZING SYSTEM...\n```")
                time.sleep(0.6)
                
                # Ghi phiên đăng nhập vào trình duyệt
                st.query_params["role"] = selected_role
                st.session_state.role = selected_role
                st.session_state.logged_in = True
                st.rerun()
                
            else:
                st.error("🚨 ACCESS DENIED: Mật khẩu không chính xác. IP đã bị lưu lại!")
                
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop() # Dừng lại, không nạp giao diện sáng bên dưới

# ==========================================
# 3. GIAO DIỆN CHÍNH THỨC SAU KHI ĐĂNG NHẬP
# ==========================================
# Ghi đè lại CSS sáng sủa, hiện đại cho phần làm việc
st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; color: #31333F; font-family: sans-serif; }
    .codx-header { background: linear-gradient(135deg, #005B9F 0%, #0078D7 100%); padding: 20px 30px; border-radius: 12px; color: white; margin-bottom: 25px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    .codx-title { font-size: 24px; font-weight: 700; margin: 0; }
    .codx-card { background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #EAECEF; }
    /* Chỉnh lại input về bình thường */
    .stTextInput input { background-color: white !important; color: black !important; border: 1px solid #ccc !important; font-family: sans-serif !important; text-align: left; font-size: 16px !important; letter-spacing: 0px;}
    .stTextInput input:focus { box-shadow: none !important; border-color: #0078D7 !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. KẾT NỐI GSHEETS & TẢI DỮ LIỆU CHỐNG LỖI 400
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
        df_raw = conn.read(spreadsheet=SPREADSHEET_URL)
        try:
            df = df_raw.iloc[:, 1:6].copy()
        except:
            df = df_raw.copy()
            
        while len(df.columns) < 5:
            df[f"Cot_Trong_{len(df.columns)}"] = ""
            
        df.columns = ["TEN_BAO_CAO", "KY_BAO_CAO", "DEADLINE", "TRANG_THAI_GOC", "DON_VI_YEU_CAU"]
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
        st.error("🚨 LỖI ĐỌC GOOGLE SHEETS. HÃY KIỂM TRA LẠI MỤC SECRETS TRÊN CLOUD VÀ QUYỀN CHIA SẺ FILE.")
        st.stop()

if "df_master" not in st.session_state:
    st.session_state.df_master = load_data()
if "editor_key" not in st.session_state:
    st.session_state.editor_key = str(uuid.uuid4())

# ==========================================
# 5. GIAO DIỆN HEADER & BỘ LỌC
# ==========================================
col_l, col_r = st.columns([1, 8])
with col_l:
    if os.path.exists("logo.png"): st.image("logo.png", width=90)
    else: st.write("📌 **LOGO**")

with col_r:
    r_txt = "Quản trị viên (Admin)" if st.session_state.role == "Admin" else "Khách (Chỉ xem)"
    st.markdown(f"""
    <div class="codx-header">
        <p class="codx-title">☑️ QUẢN TRỊ CÔNG VIỆC CÔNG AN PHƯỜNG AN KHÁNH</p>
        <p style="margin:0;">Trạng thái hệ thống: Đã kết nối | Quyền truy cập: <b>{r_txt}</b></p>
    </div>
    """, unsafe_allow_html=True)

# NÚT ĐĂNG XUẤT XÓA BỘ NHỚ TRÌNH DUYỆT
if st.sidebar.button("🚪 THOÁT / ĐĂNG XUẤT", type="primary"):
    st.query_params.clear() # Xóa lưu phiên F5
    st.session_state.clear()
    st.rerun()

with st.sidebar:
    st.header("🔍 BỘ LỌC")
    txt_search = st.text_input("Tên báo cáo:")
    
    k_list = st.session_state.df_master['KY_BAO_CAO'].unique().tolist()
    all_k = set([k for ky in k_list if isinstance(ky, str) for k in ky.split(", ")])
    sel_ky = st.multiselect("Lọc Kỳ:", list(all_k), default=list(all_k))
    
    t_list = sorted([m for m in st.session_state.df_master['THANG'].unique() if m != 0])
    t_opts = t_list + [0]
    
    def fmt_m(x):
        return f"Tháng {x}" if x != 0 else "Chưa có hạn"

    sel_thang = st.multiselect("Lọc Tháng:", options=t_opts, default=t_opts, format_func=fmt_m)
    
    tt_opts = ["🚨 TRỄ HẠN", "🔥 CẦN LÀM GẤP", "⏳ ĐANG THỰC HIỆN", "✅ HOÀN THÀNH"]
    sel_tt = st.multiselect("Trạng thái:", tt_opts, default=tt_opts)

    dv_opts = st.session_state.df_master['DON_VI_YEU_CAU'].unique().tolist()
    sel_dv = st.multiselect("Đơn vị yêu cầu:", dv_opts, default=dv_opts)
    
    st.divider()
    if st.button("🔄 Làm mới dữ liệu", use_container_width=True):
        st.cache_data.clear()
        st.session_state.df_master = load_data() 
        st.rerun()

def chk_ky(row_ky):
    if not sel_ky: return False
    return any(k in str(row_ky) for k in sel_ky)

mask = (
    st.session_state.df_master['TEN_BAO_CAO'].str.contains(txt_search, case=False, na=False) &
    st.session_state.df_master['KY_BAO_CAO'].apply(chk_ky) &
    st.session_state.df_master['THANG'].isin(sel_thang) &
    st.session_state.df_master['CANH_BAO'].isin(sel_tt) &
    st.session_state.df_master['DON_VI_YEU_CAU'].isin(sel_dv)
)
df_filtered = st.session_state.df_master[mask].copy()

# ==========================================
# 6. HIỂN THỊ BẢNG & LƯU CLOUD
# ==========================================
metric_container = st.container()
st.markdown("<br>", unsafe_allow_html=True)
col_main, col_sub = st.columns([2.4, 1.0])

with col_main:
    st.markdown('<div class="codx-card">', unsafe_allow_html=True)
    st.subheader("📋 BẢNG CÔNG VIỆC")
    
    st.markdown("###### ↕️ SẮP XẾP NHANH")
    c_s1, c_s2 = st.columns([1.5, 2])
    
    sort_opts = [
        "Mặc định", "Tên công việc", "Kỳ báo cáo", 
        "Hạn chót", "Trạng thái gốc", "Đơn vị yêu cầu báo cáo"
    ]
    with c_s1:
        sort_col = st.selectbox("Sắp xếp theo:", sort_opts)
    with c_s2:
        sort_asc = st.radio("Thứ tự:", ["Tăng (A-Z)", "Giảm (Z-A)"], horizontal=True)

    col_map = {
        "Tên công việc": "TEN_BAO_CAO", 
        "Kỳ báo cáo": "KY_BAO_CAO", 
        "Hạn chót": "DEADLINE", 
        "Trạng thái gốc": "TRANG_THAI_GOC", 
        "Đơn vị yêu cầu báo cáo": "DON_VI_YEU_CAU"
    }
    
    if sort_col != "Mặc định":
        is_asc = True if sort_asc == "Tăng (A-Z)" else False
        df_filtered = df_filtered.sort_values(
            by=col_map[sort_col], 
            ascending=is_asc, 
            na_position='last'
        )
    df_filtered = df_filtered.reset_index(drop=True)
    
    if st.session_state.role == "Admin":
        st.info("💡 Thêm/Xóa/Sửa là **TẠM THỜI**. Phải bấm **LƯU LÊN CLOUD** thì Google Sheets mới cập nhật.")
        df_filtered.insert(0, "🗑️ Xóa", False)

        c_cols = {
            "_ID": None, 
            "🗑️ Xóa": st.column_config.CheckboxColumn("🗑️ Xóa", default=False, width="small"),
            "TEN_BAO_CAO": st.column_config.TextColumn("Tên công việc", width="large"), 
            "KY_BAO_CAO": st.column_config.TextColumn("Kỳ báo cáo", width="medium"), 
            "DEADLINE": st.column_config.DateColumn("Hạn chót", format="DD/MM/YYYY", width="medium"),
            "TRANG_THAI_GOC": st.column_config.SelectboxColumn("Trạng thái", options=["Chưa xử lý", "Đang thực hiện", "Hoàn thành"], width="medium"),
            "CANH_BAO": st.column_config.TextColumn("Tình trạng", disabled=True, width="medium"),
            "DON_VI_YEU_CAU": st.column_config.TextColumn("Đơn vị yêu cầu", width="medium")
        }

        edited_df = st.data_editor(
            df_filtered[[
                "_ID", "🗑️ Xóa", "TEN_BAO_CAO", "KY_BAO_CAO", 
                "DEADLINE", "TRANG_THAI_GOC", "CANH_BAO", "DON_VI_YEU_CAU"
            ]],
            key=st.session_state.editor_key,
            use_container_width=True, 
            hide_index=True, 
            num_rows="dynamic",
            column_config=c_cols
        )

        del_ids = edited_df[edited_df["🗑️ Xóa"] == True]["_ID"].tolist()
        if del_ids:
            st.session_state.df_master = st.session_state.df_master[~st.session_state.df_master["_ID"].isin(del_ids)]
            st.rerun() 
            
        edited_df = edited_df[edited_df["🗑️ Xóa"] == False]
        for _, row in edited_df.iterrows():
            m_idx_list = st.session_state.df_master.index[st.session_state.df_master['_ID'] == row['_ID']].tolist()
            if m_idx_list:
                m_idx = m_idx_list[0]
                st.session_state.df_master.at[m_idx, 'TEN_BAO_CAO'] = row['TEN_BAO_CAO']
                st.session_state.df_master.at[m_idx, 'KY_BAO_CAO'] = row['KY_BAO_CAO']
                st.session_state.df_master.at[m_idx, 'DEADLINE'] = row['DEADLINE']
                st.session_state.df_master.at[m_idx, 'TRANG_THAI_GOC'] = row['TRANG_THAI_GOC']
                st.session_state.df_master.at[m_idx, 'DON_VI_YEU_CAU'] = row['DON_VI_YEU_CAU']
                
                t_moi = pd.to_datetime(row['DEADLINE']).month if pd.notnull(row['DEADLINE']) else 0
                st.session_state.df_master.at[m_idx, 'THANG'] = t_moi
                st.session_state.df_master.at[m_idx, 'CANH_BAO'] = phan_loai(row)

        edited_df['DEADLINE'] = pd.to_datetime(edited_df['DEADLINE'])
        edited_df['CANH_BAO'] = edited_df.apply(phan_loai, axis=1)

        # NÚT LƯU CLOUD
        st.markdown("<br>", unsafe_allow_html=True)
        col_ref, col_sv = st.columns([1, 1.5])
        
        with col_ref:
            if st.button("🔄 LÀM MỚI (HỦY SỬA LỖI)", use_container_width=True):
                st.cache_data.clear()     
                st.session_state.df_master = load_data()  
                st.rerun()                
                
        with col_sv:
            if st.button("💾 XÁC NHẬN LƯU VÀ ĐỒNG BỘ LÊN CLOUD", type="primary", use_container_width=True):
                try:
                    df_to_save = st.session_state.df_master[[
                        "TEN_BAO_CAO", "KY_BAO_CAO", "DEADLINE", 
                        "TRANG_THAI_GOC", "DON_VI_YEU_CAU"
                    ]]
                    df_upload = df_to_save.copy()
                    df_upload.insert(0, "STT_ID", range(1, len(df_upload) + 1))
                    
                    conn.update(spreadsheet=SPREADSHEET_URL, data=df_upload)
                    st.success("✅ Đã chốt hạ và đồng bộ dữ liệu thành công lên Google Sheets!")
                    st.cache_data.clear()
                    st.session_state.df_master = load_data()
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"🚨 LỖI ĐỒNG BỘ CLOUD: {e}")
    else:
        st.info("👁️ **CHẾ ĐỘ KHÁCH:** Hệ thống đang ở chế độ Chỉ Xem (Read-only).")
        
        c_cols_g = {
            "TEN_BAO_CAO": st.column_config.TextColumn("Tên công việc", width="large"), 
            "KY_BAO_CAO": st.column_config.TextColumn("Kỳ báo cáo", width="medium"), 
            "DEADLINE": st.column_config.DateColumn("Hạn chót", format="DD/MM/YYYY", width="medium"),
            "TRANG_THAI_GOC": st.column_config.TextColumn("Trạng thái", width="medium"),
            "CANH_BAO": st.column_config.TextColumn("Tình trạng", width="medium"),
            "DON_VI_YEU_CAU": st.column_config.TextColumn("Đơn vị yêu cầu", width="medium")
        }
        
        st.dataframe(
            df_filtered[[
                "TEN_BAO_CAO", "KY_BAO_CAO", "DEADLINE", 
                "TRANG_THAI_GOC", "CANH_BAO", "DON_VI_YEU_CAU"
            ]],
            use_container_width=True, 
            hide_index=True,
            column_config=c_cols_g
        )
        edited_df = df_filtered.copy()
        edited_df['DEADLINE'] = pd.to_datetime(edited_df['DEADLINE'])
        edited_df['CANH_BAO'] = edited_df.apply(phan_loai, axis=1)
        
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 7. BIỂU ĐỒ & LỊCH
# ==========================================
with metric_container:
    c_m1, c_m2, c_m3 = st.columns(3)
    tong_cv = len(edited_df)
    da_xong = len(edited_df[edited_df['CANH_BAO'] == "✅ HOÀN THÀNH"])
    tre_han = len(edited_df[edited_df['CANH_BAO'] == "🚨 TRỄ HẠN"])
    
    tl_ht = round(da_xong/tong_cv*100) if tong_cv > 0 else 0
    
    with c_m1: st.metric("TỔNG CÔNG VIỆC", tong_cv)
    with c_m2: st.metric("ĐÃ XONG", da_xong, f"{tl_ht}%")
    with c_m3: st.metric("TRỄ HẠN", tre_han, delta_color="inverse", delta="Cảnh báo")

with col_sub:
    st.markdown('<div class="codx-card">', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-weight:bold;'>📊 TỶ LỆ TIẾN ĐỘ</p>", unsafe_allow_html=True)
    
    mau_bd = {
        "✅ HOÀN THÀNH": "#10B981",
        "🚨 TRỄ HẠN": "#EF4444",
        "⏳ ĐANG THỰC HIỆN": "#3B82F6",
        "🔥 CẦN LÀM GẤP": "#F59E0B"
    }
    
    if tong_cv > 0:
        fig = px.pie(
            edited_df, 
            names='CANH_BAO', 
            hole=0.5,
            color='CANH_BAO',
            color_discrete_map=mau_bd
        )
        fig.update_layout(showlegend=False, height=200, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div><br>', unsafe_allow_html=True)

    st.markdown('<div class="codx-card">', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-weight:bold;'>📅 LỊCH NHẮC VIỆC</p>", unsafe_allow_html=True)
    
    now = datetime.datetime.now()
    cal = calendar.monthcalendar(now.year, now.month)
    df_cx = edited_df[edited_df['CANH_BAO'] != "✅ HOÀN THÀNH"].copy()
    df_cx_thang = df_cx[df_cx['DEADLINE'].dt.month == now.month]
    dls = df_cx_thang['DEADLINE'].dt.day.dropna().astype(int).unique().tolist()

    h_cal = '<table style="width:100%; border-collapse: collapse; font-size:13px; text-align:center;">'
    h_cal += '<tr><th style="color:red">CN</th><th>T2</th><th>T3</th><th>T4</th><th>T5</th><th>T6</th><th>T7</th></tr>'
    
    c_tdl = 'background:#EF4444; border: 3px solid #0078D7; color:white; border-radius:50%; width:24px; height:24px; line-height:18px; margin:auto; font-weight:bold; box-sizing:border-box;'
    c_t = 'background:#0078D7; color:white; border-radius:50%; width:24px; height:24px; line-height:24px; margin:auto; font-weight:bold;'
    c_dl = 'background:#EF4444; color:white; border-radius:50%; width:24px; height:24px; line-height:24px; margin:auto; font-weight:bold;'
    
    for week in cal:
        h_cal += '<tr>'
        for day in week:
            if day == 0: 
                h_cal += '<td style="padding: 5px;"></td>'
            elif day == now.day and day in dls: 
                h_cal += f'<td style="padding: 5px;"><div style="{c_tdl}">{day}</div></td>'
            elif day == now.day: 
                h_cal += f'<td style="padding: 5px;"><div style="{c_t}">{day}</div></td>'
            elif day in dls: 
                h_cal += f'<td style="padding: 5px;"><div style="{c_dl}">{day}</div></td>'
            else: 
                h_cal += f'<td style="padding: 5px;">{day}</td>'
        h_cal += '</tr>'
    h_cal += '</table>'
    st.markdown(h_cal, unsafe_allow_html=True)
    st.caption("🔴 Đỏ: Hạn nộp - 🔵 Xanh: Hôm nay")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 8. THÊM BÁO CÁO MỚI (ADMIN)
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
                c_t1, c_t2 = st.columns([2, 1])
                with c_t1: f_ten = st.text_input("Tên báo cáo *")
                with c_t2: f_dv = st.text_input("Đơn vị yêu cầu")
                
                c_f1, c_f2, c_f3 = st.columns([2, 1, 1])
                with c_f1: 
                    f_k = st.multiselect("Kỳ báo cáo", options=list(k_map.keys()))
                with c_f2: 
                    f_d = st.date_input("Hạn chót", value=datetime.date.today())
                with c_f3: 
                    f_tt = st.selectbox("Trạng thái", ["Chưa xử lý", "Đang thực hiện", "Hoàn thành"])
                
                if st.form_submit_button("➕ Thêm vào danh sách (Nhấn Enter)") :
                    if f_ten:
                        new_data = []
                        max_id = st.session_state.df_master['_ID'].max() if not st.session_state.df_master.empty else -1
                        dv_val = f_dv.strip() if f_dv.strip() else "Không xác định"

                        if f_k:
                            for k in f_k:
                                max_id += 1
                                m_date = k_map.get(k)
                                d_val = pd.to_datetime(m_date) if m_date else pd.to_datetime(f_d)
                                
                                new_data.append({
                                    "_ID": max_id, "TEN_BAO_CAO": f_ten, 
                                    "KY_BAO_CAO": k, "DEADLINE": d_val, 
                                    "TRANG_THAI_GOC": f_tt, "DON_VI_YEU_CAU": dv_val
                                })
                        else:
                            max_id += 1
                            new_data.append({
                                "_ID": max_id, "TEN_BAO_CAO": f_ten, 
                                "KY_BAO_CAO": "Không xác định", "DEADLINE": pd.to_datetime(f_d), 
                                "TRANG_THAI_GOC": f_tt, "DON_VI_YEU_CAU": dv_val
                            })

                        n_df = pd.DataFrame(new_data)
                        n_df['THANG'] = n_df['DEADLINE'].dt.month.fillna(0).astype(int)
                        n_df['CANH_BAO'] = n_df.apply(phan_loai, axis=1)
                        st.session_state.df_master = pd.concat(
                            [st.session_state.df_master, n_df], 
                            ignore_index=True
                        )
                        st.rerun()