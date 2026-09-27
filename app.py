import os
from datetime import datetime
import pandas as pd
import streamlit as st
st.image("IMG_20260927_111652.jpg")
# Cấu hình trang
st.set_page_config(page_title="Hệ Thống Dọn Phòng", layout="wide", page_icon="🧹")

# File dữ liệu lưu trữ
CSV_FILE = "room_cleaning.csv"
ROOM_STATUS_FILE = "rooms.csv"

# Danh sách phòng mặc định
DEFAULT_ROOMS = [
    {"Phòng": f"P.{100 + i}", "Loại": "Đơn", "Tầng": "Tầng 1"} for i in range(1, 6)
] + [
    {"Phòng": f"P.{200 + i}", "Loại": "Đôi", "Tầng": "Tầng 2"} for i in range(1, 6)
] + [
    {"Phòng": f"P.{300 + i}", "Loại": "VIP", "Tầng": "Tầng 3"} for i in range(1, 6)
]

# Trạng thái phòng hợp lệ
STATUS_OPTIONS = ["Trống - Sạch", "Đang ở", "Cần dọn", "Đang dọn", "Bảo trì"]
STAFF_LIST = ["Nguyễn Văn A", "Trần Thị B", "Lê Văn C", "Chưa phân công"]

# 1. Khởi tạo dữ liệu phòng
if "rooms_df" not in st.session_state:
    if os.path.exists(ROOM_STATUS_FILE):
        try:
            st.session_state.rooms_df = pd.read_csv(ROOM_STATUS_FILE)
        except Exception:
            st.session_state.rooms_df = pd.DataFrame(DEFAULT_ROOMS)
            st.session_state.rooms_df["Trạng thái"] = "Trống - Sạch"
            st.session_state.rooms_df["Nhân viên"] = "Chưa phân công"
            st.session_state.rooms_df["Cập nhật cuối"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    else:
        df_init = pd.DataFrame(DEFAULT_ROOMS)
        df_init["Trạng thái"] = "Trống - Sạch"
        df_init["Nhân viên"] = "Chưa phân công"
        df_init["Cập nhật cuối"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        st.session_state.rooms_df = df_init

# 2. Khởi tạo nhật ký dọn dẹp
if "history" not in st.session_state:
    if os.path.exists(CSV_FILE):
        try:
            df_loaded = pd.read_csv(CSV_FILE)
            st.session_state.history = df_loaded.to_dict(orient="records")
        except Exception:
            st.session_state.history = []
    else:
        st.session_state.history = []

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# Lưu trạng thái phòng xuống file
def save_room_status():
    st.session_state.rooms_df.to_csv(ROOM_STATUS_FILE, index=False, encoding="utf-8-sig_Ms Quinh")

# Lưu lịch sử xuống file
def save_history():
    df_hist = pd.DataFrame(st.session_state.history)
    df_hist.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")

# --- DANH MỤC ĐIỀU HƯỚNG ---
page = st.sidebar.radio("📋 Chọn trang hệ thống", ["🧹 Quản Lý Dọn Phòng", "🔑 Admin & Báo Cáo"])

# ---------------------------------------------------------
# TRANG 1: QUẢN LÝ DỌN PHÒNG (Dành cho Lễ tân & Buồng phòng)
# ---------------------------------------------------------
if page == "🧹 Quản Lý Dọn Phòng":
    st.title("🧹 Theo Dõi & Cập Nhật Trạng Thái Dọn Phòng")
    st.caption("Quản lý trạng thái vệ sinh phòng thời gian thực")

    # Tổng quan chỉ số nhanh
    df_r = st.session_state.rooms_df
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🟢 Sạch sẵn sàng", len(df_r[df_r["Trạng thái"] == "Trống - Sạch"]))
    m2.metric("🧹 Cần dọn", len(df_r[df_r["Trạng thái"] == "Cần dọn"]))
    m3.metric("⏳ Đang dọn", len(df_r[df_r["Trạng thái"] == "Đang dọn"]))
    m4.metric("🔴 Đang có khách", len(df_r[df_r["Trạng thái"] == "Đang ở"]))

    st.markdown("---")

    col_left, col_right = st.columns([1.2, 1])

    # Khối 1: Cập nhật trạng thái
    with col_left:
        st.subheader("📝 Cập nhật trạng thái phòng")
        
        selected_room = st.selectbox("🛏️ Chọn phòng:", df_r["Phòng"].tolist())
        
        # Lấy thông tin phòng hiện tại
        current_info = df_r[df_r["Phòng"] == selected_room].iloc[0]
        st.info(f"Trạng thái hiện tại: **{current_info['Trạng thái']}** | NV: **{current_info['Nhân viên']}**")

        new_status = st.selectbox("🔄 Trạng thái mới:", STATUS_OPTIONS, index=STATUS_OPTIONS.index(current_info['Trạng thái']))
        assigned_staff = st.selectbox("👤 Nhân viên phụ trách:", STAFF_LIST, index=STAFF_LIST.index(current_info['Nhân viên']) if current_info['Nhân viên'] in STAFF_LIST else 0)
        note = st.text_input("📝 Ghi chú (VD: Thiếu khăn, hỏng bóng đèn...):", "")

        if st.button("💾 Lưu Cập Nhật"):
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Cập nhật DataFrame phòng
            idx = st.session_state.rooms_df[st.session_state.rooms_df["Phòng"] == selected_room].index[0]
            st.session_state.rooms_df.at[idx, "Trạng thái"] = new_status
            st.session_state.rooms_df.at[idx, "Nhân viên"] = assigned_staff
            st.session_state.rooms_df.at[idx, "Cập nhật cuối"] = now_str
            save_room_status()

            # Thêm vào nhật ký hoạt động
            st.session_state.history.append({
                "Thời gian": now_str,
                "Phòng": selected_room,
                "Trạng thái mới": new_status,
                "Nhân viên": assigned_staff,
                "Ghi chú": note
            })
            save_history()

            st.success(f"Đã cập nhật {selected_room} sang '{new_status}'!")
            st.rerun()

    # Khối 2: Sơ đồ phòng hiện tại
    with col_right:
        st.subheader("📌 Danh sách phòng hiện tại")
        
        # Bộ lọc tầng
        filter_floor = st.selectbox("Lọc theo tầng:", ["Tất cả"] + list(df_r["Tầng"].unique()))
        
        df_display = df_r.copy()
        if filter_floor != "Tất cả":
            df_display = df_display[df_display["Tầng"] == filter_floor]

        # Định dạng màu sắc trực quan
        def highlight_status(val):
            color_map = {
                "Trống - Sạch": "background-color: #d4edda; color: #155724;",
                "Cần dọn": "background-color: #f8d7da; color: #721c24;",
                "Đang dọn": "background-color: #fff3cd; color: #856404;",
                "Đang ở": "background-color: #cce5ff; color: #004085;",
                "Bảo trì": "background-color: #e2e3e5; color: #383d41;"
            }
            return color_map.get(val, "")

        st.dataframe(
            df_display.style.map(highlight_status, subset=["Trạng thái"]),
            use_container_width=True,
            hide_index=True
        )

# ---------------------------------------------------------
# TRANG 2: ADMIN & BÁO CÁO THỐNG KÊ
# ---------------------------------------------------------
elif page == "🔑 Admin & Báo Cáo":
    st.title("🔑 Trang Quản Trị & Thống Kê Buồng Phòng")

    if not st.session_state.admin_logged_in:
        with st.form("admin_login_form"):
            password = st.text_input("Nhập mật khẩu quản trị", type="password")
            login_submitted = st.form_submit_button("🔑 Đăng nhập")

            if login_submitted:
                if password == "123456":
                    st.session_state.admin_logged_in = True
                    st.success("Đăng nhập thành công!")
                    st.rerun()
                else:
                    st.error("Mật khẩu không chính xác!")
        st.stop()

    # Header Admin
    c_title, c_logout = st.columns([4, 1])
    with c_title:
        st.success("Đã xác thực quyền Quản trị viên")
    with c_logout:
        if st.button("🔒 Đăng xuất"):
            st.session_state.admin_logged_in = False
            st.rerun()

    tab1, tab2, tab3 = st.tabs([
        "🏨 Sơ Đồ Toàn Bộ Phòng", 
        "📊 Thống Kê & Hiệu Suất", 
        "📜 Nhật Ký Hoạt Động"
    ])

    # TAB 1: SƠ ĐỒ TOÀN BỘ PHÒNG
    with tab1:
        st.subheader("Sơ đồ quản lý trạng thái realtime")
        st.dataframe(st.session_state.rooms_df, use_container_width=True, hide_index=True)

    # TAB 2: THỐNG KÊ
    with tab2:
        st.subheader("Thống kê hoạt động dọn phòng")
        
        df_hist = pd.DataFrame(st.session_state.history)
        
        if not df_hist.empty:
            col_chart1, col_chart2 = st.columns(2)

            with col_chart1:
                st.write("**Số lượt dọn/chuyển trạng thái theo Nhân viên:**")
                staff_counts = df_hist["Nhân viên"].value_counts()
                st.bar_chart(staff_counts)

            with col_chart2:
                st.write("**Số lượt cập nhật theo Phòng:**")
                room_counts = df_hist["Phòng"].value_counts()
                st.bar_chart(room_counts)
        else:
            st.info("Chưa có lịch sử hoạt động được ghi nhận.")

    # TAB 3: NHẬT KÝ CHI TIẾT
    with tab3:
        st.subheader("Chi tiết nhật ký thay đổi trạng thái")
        df_hist = pd.DataFrame(st.session_state.history)
        if not df_hist.empty:
            st.dataframe(df_hist, use_container_width=True, hide_index=True)
            
            # Nút xuất dữ liệu
            csv_data = df_hist.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
            st.download_button(
                label="📥 Tải nhật ký CSV",
                data=csv_data,
                file_name=f"lich_su_don_phong_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )
        else:
            st.info("Nhật ký đang trống.")
