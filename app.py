import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import threading
import pytz
import base64
import os
from supabase import create_client

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# ============================================================
# CONFIG
# ============================================================
LOGIN_API_URL = "https://script.google.com/macros/s/AKfycbyagL0weEesEjs1RohprP2_OF5heaHGKoxE_AWk7SCmveFWl6k-2vM2wXUVQgBaX4emew/exec"

# ============================================================
# CREATE ORDER API
# EXISTING CREATE ORDER BACKEND
# ============================================================
CREATE_ORDER_API_URL = "https://script.google.com/macros/s/AKfycbzoeuciiCqzwm6O_UHv-h_R8wkdeEX0TMTUSV64Ho1T-Ut3YoBw5rB3JtT0Sx8hkm4U/exec"

# ============================================================
# ORDER ACTIVITY API
# NEW SEPARATE ORDER ACTIVITY BACKEND
# ============================================================
ORDER_ACTIVITY_API_URL = "https://script.google.com/macros/s/AKfycbw03zjKkyX8vXIY3cmr5E7Rmn7uIdhj87yK1Xif8VgvGW3UvcAsrMSwvHHZDSYp9xxO/exec"

STOCK_URL = "https://docs.google.com/spreadsheets/d/1AalnQ8HBiLYo4tgpKUtyk6aCc9k4ZJTO8n74UizaBig/export?format=csv&gid=0"
OD_URL = "https://docs.google.com/spreadsheets/d/1piSm1HMO0PFzW28PIChPgULJoL8n5cjg_HUi7bZBwJ8/export?format=csv&gid=81459910"
PHOTO_URL = "https://docs.google.com/spreadsheets/d/12vBtZzZil_8NKtb3GgrIvmzUHGDWeXpvgR3XhFbXudI/export?format=csv&gid=719185942"

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Retail Order Management",
    page_icon="📦",
    layout="wide"
)

# ============================================================
# GLOBAL STYLING
# ============================================================
st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-family: "Segoe UI", "Inter", -apple-system, sans-serif;
    }
    .stApp {
        background: linear-gradient(180deg, #fafbfc 0%, #f4f6f9 100%);
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1f2937 0%, #111827 100%);
    }
    section[data-testid="stSidebar"] * {
        color: #f3f4f6 !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.12) !important;
    }
    section[data-testid="stSidebar"] .stButton button {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.12);
        color: #f3f4f6;
        border-radius: 10px;
        text-align: left;
        transition: all 0.15s ease-in-out;
        font-weight: 500;
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        background: #7c3aed;
        border-color: #7c3aed;
        color: #ffffff;
        transform: translateX(2px);
    }
    h1, h2, h3 {
        font-weight: 700 !important;
        color: #111827;
    }
    h1 {
        letter-spacing: -0.5px;
    }
    .main .stButton button {
        border-radius: 10px;
        font-weight: 600;
        border: 1px solid #e5e7eb;
        transition: all 0.15s ease-in-out;
    }
    .main .stButton button:hover {
        border-color: #7c3aed;
        color: #7c3aed;
        box-shadow: 0 2px 10px rgba(124,58,237,0.15);
    }
    div[data-testid="stFormSubmitButton"] button,
    .main .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #7c3aed, #5b21b6);
        color: white !important;
        border: none;
    }
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #ececec;
        border-radius: 14px;
        padding: 1rem 1.2rem;
        box-shadow: 0 4px 14px rgba(0,0,0,0.04);
    }
    div[data-testid="stMetric"] label {
        font-weight: 600;
        color: #6b7280 !important;
    }
    button[data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        font-weight: 600;
        padding: 0.5rem 1.2rem;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: #f3e8ff;
        color: #7c3aed !important;
    }
    .stTextInput input,
    .stNumberInput input,
    .stSelectbox div[data-baseweb="select"],
    .stDateInput input {
        border-radius: 10px !important;
    }
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #ececec;
    }
    div[data-testid="stAlert"] {
        border-radius: 12px;
    }
    hr {
        margin: 1.2rem 0;
        opacity: 0.5;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 18px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# SESSION STATE
# ============================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "role" not in st.session_state:
    st.session_state.role = ""
if "user_parties" not in st.session_state:
    st.session_state.user_parties = []
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "cart" not in st.session_state:
    st.session_state.cart = []
if "last_sku" not in st.session_state:
    st.session_state.last_sku = None
if "form_version" not in st.session_state:
    st.session_state.form_version = 0
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "submitted_by" not in st.session_state:
    st.session_state.submitted_by = ""

# ============================================================
# ORDER ACTIVITY DATE STATES
# ============================================================
if "billed_date" not in st.session_state:
    st.session_state.billed_date = None
if "pending_date" not in st.session_state:
    st.session_state.pending_date = None
if "cancelled_date" not in st.session_state:
    st.session_state.cancelled_date = None

# ============================================================
# RESTORE LOGIN AFTER BROWSER REFRESH
# ============================================================
if not st.session_state.logged_in:
    qp = st.query_params
    if "u" in qp and "n" in qp:
        st.session_state.logged_in = True
        st.session_state.username = qp.get("u", "")
        st.session_state.user_name = qp.get("n", "")
        st.session_state.role = qp.get("r", "")
        parties_str = qp.get("p", "")
        st.session_state.user_parties = (
            parties_str.split("~")
            if parties_str
            else []
        )

# ============================================================
# DATE / TIME
# ============================================================
ist = pytz.timezone("Asia/Kolkata")
now_ist = datetime.now(ist)
date_time = now_ist.strftime(
    "%d-%m-%Y %H:%M:%S"
)

# ============================================================
# SESSION-LEVEL CACHE HELPER
# Fetches only once per session (on first need / after login,
# or after login/logout, or when user manually hits Refresh).
# Page switches (Dashboard <-> Stock <-> OD <-> Photo <-> Order
# Activity) will NOT trigger a re-fetch since data already
# sits in st.session_state.
# ============================================================
def get_cached(key, loader_fn, *args, **kwargs):
    if key not in st.session_state:
        st.session_state[key] = loader_fn(*args, **kwargs)
    return st.session_state[key]


def clear_all_cached_data():
    """Used by the sidebar Refresh button to force fresh fetch everywhere."""
    keys_to_clear = [
        k for k in st.session_state.keys()
        if k.startswith("cached_")
    ]
    for k in keys_to_clear:
        del st.session_state[k]
    # Also clear underlying st.cache_data caches so a truly fresh
    # network/sheet fetch happens, not just a session-state repopulation.
    st.cache_data.clear()

# ============================================================
# LOAD STOCK
# ============================================================
# ============================================================
# LOAD STOCK FROM SUPABASE
# ============================================================
@st.cache_data(ttl=120)
def load_stock():

    try:

        response = (
            supabase
            .table("stock")
            .select("*")
            .execute()
        )

        rows = response.data or []

        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame(rows)

        # ====================================================
        # SAVE SUPABASE AUTHORITATIVE VALUES
        # ====================================================

        supabase_farukhnagar = pd.to_numeric(
            df["farukhnagar"],
            errors="coerce"
        ).fillna(0)

        supabase_mumbai = pd.to_numeric(
            df["mumbai_stock"],
            errors="coerce"
        ).fillna(0)

        supabase_l3 = pd.to_numeric(
            df["l3_stock"],
            errors="coerce"
        ).fillna(0)

        supabase_sku = (
            df["sku_code"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        supabase_product = (
            df["product_name"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        supabase_status = (
            df["status"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        supabase_subcategory = (
            df["sub_category"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        supabase_hsn = (
            df["hsn_code"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        supabase_mrp = pd.to_numeric(
            df["mrp"],
            errors="coerce"
        ).fillna(0)

        # ====================================================
        # RESTORE COMPLETE GOOGLE SHEET ROW
        # ====================================================

        if "row_data" in df.columns:

            row_data_df = pd.json_normalize(
                df["row_data"]
            )

            row_data_df.columns = (
                row_data_df.columns
                .astype(str)
                .str.strip()
                .str.upper()
            )

        else:

            row_data_df = pd.DataFrame(
                index=df.index
            )

        # ====================================================
        # FORCE REQUIRED COLUMNS FROM SUPABASE
        # ====================================================

        row_data_df["SKU CODE"] = supabase_sku.values

        row_data_df["PRODUCT NAME"] = (
            supabase_product.values
        )

        row_data_df["STATUS"] = (
            supabase_status.values
        )

        row_data_df["SUB CATEGORY"] = (
            supabase_subcategory.values
        )

        row_data_df["FARUKHNAGAR"] = (
            supabase_farukhnagar.values
        )

        row_data_df["MUMBAI STOCK"] = (
            supabase_mumbai.values
        )

        row_data_df["L3 STOCK"] = (
            supabase_l3.values
        )

        row_data_df["HSN CODE"] = (
            supabase_hsn.values
        )

        row_data_df["MRP"] = (
            supabase_mrp.values
        )

        df = row_data_df

        # ====================================================
        # CLEAN DATA
        # ====================================================

        df = df.dropna(
            how="all"
        ).copy()

        if "PRODUCT NAME" in df.columns:

            product_check = (
                df["PRODUCT NAME"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

            df = df[
                product_check != ""
            ].copy()

        # ====================================================
        # SKU
        # ====================================================

        if "SKU CODE" in df.columns:

            df["SKU"] = (
                df["SKU CODE"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

        # ====================================================
        # NUMERIC STOCK COLUMNS
        # ====================================================

        for col in [
            "FARUKHNAGAR",
            "MUMBAI STOCK",
            "L3 STOCK",
            "MRP"
        ]:

            if col in df.columns:

                df[col] = pd.to_numeric(
                    df[col],
                    errors="coerce"
                ).fillna(0)

        # ====================================================
        # FINAL COLUMN CLEAN
        # ====================================================

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.upper()
        )

        return df

    except Exception as e:

        raise Exception(
            f"Supabase Stock load error: {e}"
        )

# ============================================================
# LOAD OD / OUTSTANDING DATA
# ============================================================
# ============================================================
# LOAD OD / OUTSTANDING DATA FROM SUPABASE
# ============================================================
@st.cache_data(ttl=120)
def load_od_status():

    try:

        response = (
            supabase
            .table("od_status")
            .select(
                "party_name,"
                "od,"
                "ofl,"
                "not_due,"
                "grand_total,"
                "credit_limit,"
                "zone,"
                "balance_limit"
            )
            .execute()
        )

        rows = response.data or []

        if not rows:
            return pd.DataFrame(
                columns=[
                    "PARTY NAME",
                    "OD",
                    "OFL",
                    "NOT DUE",
                    "GRAND TOTAL",
                    "CREDIT LIMIT",
                    "ZONE",
                    "BALANCE LIMIT"
                ]
            )

        df = pd.DataFrame(rows)

        # Supabase column names
        # → existing app column names
        df = df.rename(
            columns={
                "party_name": "PARTY NAME",
                "od": "OD",
                "ofl": "OFL",
                "not_due": "NOT DUE",
                "grand_total": "GRAND TOTAL",
                "credit_limit": "CREDIT LIMIT",
                "zone": "ZONE",
                "balance_limit": "BALANCE LIMIT"
            }
        )

        # Same cleanup as old Google Sheet logic
        df["PARTY NAME"] = (
            df["PARTY NAME"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        df = df[
            df["PARTY NAME"].str.upper() != "TOTAL"
        ].copy()

        return df

    except Exception as e:

        raise Exception(
            f"Supabase OD data load error: {e}"
        )

# ============================================================
# LOGIN FUNCTION
# ============================================================
def login_user(username, password):
    try:
        response = (
            supabase
            .table("users")
            .select("username, name, role, active")
            .eq("username", username)
            .eq("password", password)
            .eq("active", True)
            .limit(1)
            .execute()
        )

        rows = response.data or []

        if not rows:
            return {
                "success": False,
                "message": "Invalid username or password ❌"
            }

        user = rows[0]

        return {
            "success": True,
            "username": user.get("username", ""),
            "name": user.get("name", ""),
            "role": user.get("role", "")
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Supabase login error: {e}"
        }

# ============================================================
# USER MAPPING FUNCTION
# ============================================================
def get_user_mapping(username):

    try:

        response = (
            supabase
            .table("user_parties")
            .select("party_name")
            .eq("username", username)
            .execute()
        )

        rows = response.data or []

        parties = []

        for row in rows:

            party = str(
                row.get("party_name", "")
            ).strip()

            if party:
                parties.append(party)

        # Remove duplicates
        parties = list(dict.fromkeys(parties))

        return {
            "success": True,
            "username": username,
            "parties": parties,
            "count": len(parties)
        }

    except Exception as e:

        return {
            "success": False,
            "message": f"Supabase user mapping error: {e}"
        }

# ============================================================
# SEND ORDER DATA
# CREATE ORDER ONLY
# ============================================================
def send_data(payload):
    try:
        requests.post(
            CREATE_ORDER_API_URL,
            json=payload,
            timeout=5
        )
    except Exception:
        pass

# ============================================================
# GET ORDER ACTIVITY FROM SUPABASE
# ============================================================
@st.cache_data(ttl=30)
def get_order_activity(parties):

    try:

        query = (
            supabase
            .table("orders")
            .select(
                "order_date,"
                "user_name,"
                "party,"
                "sku,"
                "qty,"
                "final_status"
            )
        )

        # ----------------------------------------------------
        # NORMAL USER → ONLY MAPPED PARTIES
        # ADMIN → ALL ORDERS
        # ----------------------------------------------------
        if parties:
            query = query.in_(
                "party",
                list(parties)
            )

        # Latest orders first
        query = query.order(
            "order_date",
            desc=True
        )

        response = query.execute()

        rows = response.data or []

        # ----------------------------------------------------
        # CONVERT SUPABASE COLUMNS TO EXISTING APP COLUMNS
        # ----------------------------------------------------
        order_data = []

        for row in rows:

            order_data.append({

                "DATE": row.get(
                    "order_date",
                    ""
                ),

                "USER": row.get(
                    "user_name",
                    ""
                ),

                "PARTY": row.get(
                    "party",
                    ""
                ),

                "SKU": row.get(
                    "sku",
                    ""
                ),

                "QTY": row.get(
                    "qty",
                    0
                ),

                "FINAL STATUS": row.get(
                    "final_status",
                    ""
                )

            })

        return {
            "success": True,
            "data": order_data
        }

    except Exception as e:

        return {
            "success": False,
            "message": (
                f"Supabase Order Activity error: {e}"
            )
        }

# ============================================================
# LOAD SKU PHOTOS
# ============================================================
@st.cache_data(ttl=120)
def load_sku_photos():
    df = pd.read_csv(
        PHOTO_URL
    )
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.upper()
    )
    df = df.dropna(
        how="all"
    ).copy()
    if "SKU CODE" in df.columns:
        df["SKU CODE"] = (
            df["SKU CODE"]
            .fillna("")
            .astype(str)
            .str.strip()
        )
    if "IMAGE URL" in df.columns:
        df["IMAGE URL"] = (
            df["IMAGE URL"]
            .fillna("")
            .astype(str)
            .str.strip()
        )
        def convert_drive_link(url):
            if not url:
                return url
            file_id = None
            if "id=" in url:
                file_id = (
                    url
                    .split("id=")[-1]
                    .split("&")[0]
                    .strip()
                )
            elif "/file/d/" in url:
                file_id = (
                    url
                    .split("/file/d/")[-1]
                    .split("/")[0]
                    .strip()
                )
            if file_id:
                return (
                    "https://drive.google.com/thumbnail"
                    f"?id={file_id}&sz=w1000"
                )
            return url
        df["IMAGE URL"] = df["IMAGE URL"].apply(
            convert_drive_link
        )
    return df

# ============================================================
# LOGIN PAGE
# ============================================================
if not st.session_state.logged_in:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
            padding-left: 0rem;
            padding-right: 0rem;
            max-width: 100%;
        }
        .stApp {
            background:
                radial-gradient(
                    circle at 25% 20%,
                    rgba(255,255,255,0.10),
                    transparent 45%
                ),
                radial-gradient(
                    circle at 80% 75%,
                    rgba(255,210,255,0.10),
                    transparent 50%
                ),
                linear-gradient(
                    160deg,
                    #241b3a 0%,
                    #3f2b64 35%,
                    #6a4a95 65%,
                    #9b6bb0 100%
                ) !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"] {
            border: 1px solid rgba(255,255,255,0.35) !important;
            box-shadow: 0 25px 60px rgba(0,0,0,0.35) !important;
            padding: 2.6rem 2.4rem !important;
            border-radius: 24px !important;
            max-width: 400px;
            margin: 0 auto;
            background: rgba(255,255,255,0.12) !important;
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
        }
        .login-title-white {
            text-align: center;
            color: #ffffff;
            font-size: 2.1rem;
            font-weight: 800;
            letter-spacing: 0.5px;
            margin-bottom: 0.3rem;
        }
        .login-subtitle-white {
            text-align: center;
            color: rgba(255,255,255,0.75);
            font-size: 0.85rem;
            margin-bottom: 1.6rem;
        }
        .stTextInput input {
            background: transparent !important;
            border: none !important;
            border-bottom: 1px solid rgba(255,255,255,0.45) !important;
            border-radius: 0px !important;
            color: #111827 !important;
            padding: 0.5rem 0.2rem !important;
        }
        .stTextInput input::placeholder {
            color: #111827 !important;
            opacity: 1 !important;
        }
        .stTextInput label {
            color: rgba(255,255,255,0.8) !important;
            font-size: 0.75rem !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .main .stCheckbox label p {
            color: rgba(255,255,255,0.85) !important;
            font-size: 0.85rem !important;
        }
        .login-forgot-text {
            color: rgba(255,255,255,0.75);
            font-size: 0.85rem;
            text-align: right;
        }
        .main .stButton button {
            background: #ffffff !important;
            color: #4a2f7a !important;
            border: none !important;
            border-radius: 30px !important;
            font-weight: 700 !important;
            padding: 0.65rem 0 !important;
        }
        .main .stButton button:hover {
            box-shadow: 0 0 18px rgba(255,255,255,0.5) !important;
            color: #4a2f7a !important;
        }
        .login-footer-note {
            text-align: center;
            color: rgba(255,255,255,0.7);
            font-size: 0.85rem;
            margin-top: 0.8rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='height:9vh;'></div>",
        unsafe_allow_html=True
    )
    center_col_left, center_col_mid, center_col_right = st.columns(
        [1, 1.3, 1]
    )
    with center_col_mid:
        form_box = st.container(
            border=True
        )
        with form_box:
            st.markdown(
                "<div class='login-title-white'>Login</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<div class='login-subtitle-white'>"
                "Retail Order Management — sign in to continue"
                "</div>",
                unsafe_allow_html=True
            )
            username = st.text_input(
                "Username",
                placeholder="Enter username"
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter password"
            )
            row_col1, row_col2 = st.columns(
                [1, 1]
            )
            with row_col1:
                remember_me = st.checkbox(
                    "Remember Me",
                    value=True
                )
            with row_col2:
                st.markdown(
                    "<div class='login-forgot-text'>"
                    "Forgot password? Contact admin"
                    "</div>",
                    unsafe_allow_html=True
                )
            st.markdown(
                "<div style='height:0.5rem;'></div>",
                unsafe_allow_html=True
            )
            login_clicked = st.button(
                "Login",
                use_container_width=True
            )
            st.markdown(
                "<div class='login-footer-note'>"
                "Need access? Contact your admin"
                "</div>",
                unsafe_allow_html=True
            )
        if login_clicked:
            if not username:
                st.warning(
                    "Username enter karo ❌"
                )
            elif not password:
                st.warning(
                    "Password enter karo ❌"
                )
            else:
                with st.spinner(
                    "🔐 Logging... Please Wait!"
                ):
                    result = login_user(
                        username,
                        password
                    )
                    if result.get("success"):
                        st.session_state.logged_in = True
                        st.session_state.username = (
                            result.get(
                                "username",
                                ""
                            )
                        )
                        st.session_state.user_name = (
                            result.get(
                                "name",
                                ""
                            )
                        )
                        st.session_state.role = (
                            result.get(
                                "role",
                                ""
                            )
                        )
                        mapping_result = get_user_mapping(
                            st.session_state.username
                        )
                        if mapping_result.get("success"):
                            st.session_state.user_parties = (
                                mapping_result.get(
                                    "parties",
                                    []
                                )
                            )
                        else:
                            st.session_state.user_parties = []
                        st.session_state.page = "Dashboard"
                        # Fresh login -> make sure any stale cached_*
                        # data from a previous session/user is wiped so
                        # the very first load after login is fresh.
                        clear_all_cached_data()
                        if remember_me:
                            st.query_params["u"] = (
                                st.session_state.username
                            )
                            st.query_params["n"] = (
                                st.session_state.user_name
                            )
                            st.query_params["r"] = (
                                st.session_state.role
                            )
                            st.query_params["p"] = "~".join(
                                st.session_state.user_parties
                            )
                if st.session_state.logged_in:
                    st.rerun()
                elif not result.get("success"):
                    st.error(
                        result.get(
                            "message",
                            "Login failed ❌"
                        )
                    )

# ============================================================
# MAIN APPLICATION
# ============================================================
else:
    # ========================================================
    # SIDEBAR
    # ========================================================
    with st.sidebar:
        st.title("📦 Retail App")
        st.divider()
        st.write(
            f"👤 **{st.session_state.user_name}**"
        )
        st.caption(
            st.session_state.role
        )
        st.divider()
        st.subheader("Navigation")
        # DASHBOARD
        if st.button(
            "🏠 Dashboard",
            use_container_width=True
        ):
            st.session_state.page = "Dashboard"
            st.rerun()
        # CREATE ORDER
        if st.session_state.role.strip().upper() != "ADMIN":
            if st.button(
                "📦 Create Order",
                use_container_width=True
            ):
                st.session_state.page = "Create Order"
                st.rerun()
        # ORDER ACTIVITY
        if st.button(
            "📋 Order Activity",
            use_container_width=True
        ):
            st.session_state.page = "Order Activity"
            st.rerun()
        # STOCK
        if st.button(
            "📊 Stock",
            use_container_width=True
        ):
            st.session_state.page = "Stock"
            st.rerun()
        # OD STATUS
        if st.button(
            "💰 OD Status",
            use_container_width=True
        ):
            st.session_state.page = "OD Status"
            st.rerun()
        # SKU PHOTO
        if st.button(
            "📸 SKU Photo",
            use_container_width=True
        ):
            st.session_state.page = "SKU Photo"
            st.rerun()
        st.divider()
        # REFRESH DATA
        if st.button(
            "🔄 Refresh Data",
            use_container_width=True
        ):
            clear_all_cached_data()
            st.toast("Data refreshed ✅")
            st.rerun()
        st.divider()
        # LOGOUT
        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):
            st.session_state.clear()
            st.query_params.clear()
            st.rerun()
    # ========================================================
    # DASHBOARD
    # ========================================================
    if st.session_state.page == "Dashboard":
        st.title("🏠 Dashboard")
        st.success(
            f"Welcome {st.session_state.user_name} 👋"
        )
        st.divider()
        dash_is_admin = (
            st.session_state.role.strip().upper()
            == "ADMIN"
        )
        dash_total_qty = 0
        dash_billed_qty = 0
        dash_pending_qty = 0
        try:
            with st.spinner(
                "Loading dashboard summary..."
            ):
                dash_parties_key = (
                    ()
                    if dash_is_admin
                    else tuple(
                        st.session_state.user_parties
                    )
                )
                dash_result = get_cached(
                    f"cached_order_activity_{dash_is_admin}_{dash_parties_key}",
                    get_order_activity,
                    dash_parties_key
                )
            if dash_result.get("success"):
                dash_data = dash_result.get(
                    "data",
                    []
                )
                if dash_data:
                    dash_df = pd.DataFrame(
                        dash_data
                    )
                    dash_df.columns = (
                        dash_df.columns
                        .astype(str)
                        .str.strip()
                        .str.upper()
                    )
                    if (
                        "PARTY" in dash_df.columns
                        and "FINAL STATUS" in dash_df.columns
                        and "QTY" in dash_df.columns
                    ):
                        dash_df["PARTY"] = (
                            dash_df["PARTY"]
                            .fillna("")
                            .astype(str)
                            .str.strip()
                        )
                        if not dash_is_admin:
                            dash_mapped_parties = [
                                str(p).strip()
                                for p in
                                st.session_state.user_parties
                            ]
                            dash_df = dash_df[
                                dash_df["PARTY"].isin(
                                    dash_mapped_parties
                                )
                            ].copy()
                        dash_df["FINAL STATUS"] = (
                            dash_df["FINAL STATUS"]
                            .fillna("")
                            .astype(str)
                            .str.strip()
                            .str.upper()
                        )
                        dash_df["QTY"] = pd.to_numeric(
                            dash_df["QTY"],
                            errors="coerce"
                        ).fillna(0)
                        dash_billed_statuses = [
                            "PUNCHED IN L1",
                            "PUNCHED IN L3"
                        ]
                        dash_cancelled_statuses = [
                            "CANCELLED"
                        ]
                        dash_total_qty = (
                            dash_df["QTY"].sum()
                        )
                        dash_billed_qty = (
                            dash_df.loc[
                                dash_df["FINAL STATUS"].isin(
                                    dash_billed_statuses
                                ),
                                "QTY"
                            ].sum()
                        )
                        dash_pending_mask = (
                            ~dash_df["FINAL STATUS"].isin(
                                dash_billed_statuses
                                + dash_cancelled_statuses
                            )
                        )
                        dash_pending_qty = (
                            dash_df.loc[
                                dash_pending_mask,
                                "QTY"
                            ].sum()
                        )
        except Exception:
            dash_total_qty = 0
            dash_billed_qty = 0
            dash_pending_qty = 0
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "📦 Total Orders Qty",
                int(dash_total_qty)
            )
        with col2:
            st.metric(
                "✅ Total Billed Qty",
                int(dash_billed_qty)
            )
        with col3:
            st.metric(
                "⏳ Total Pending Qty",
                int(dash_pending_qty)
            )
        with col4:
            st.metric(
                "🏪 Mapped Parties",
                len(
                    st.session_state.user_parties
                )
            )
        st.divider()
        st.subheader(
            "👤 User Information"
        )
        col1, col2 = st.columns(2)
        with col1:
            st.write(
                f"**Username:** "
                f"{st.session_state.username}"
            )
        with col2:
            st.write(
                f"**Role:** "
                f"{st.session_state.role}"
            )
        st.subheader(
            "🏪 Party Access"
        )
        st.info(
            f"You have access to "
            f"**{len(st.session_state.user_parties)} parties**."
        )
    # ========================================================
    # CREATE ORDER
    # ========================================================
    elif st.session_state.page == "Create Order":
        st.title("📦 Create Order")
        st.caption(
            f"Order Date: {date_time}"
        )
        if st.session_state.submitted:
            st.balloons()
            st.success(
                "Order Submitted Successfully 🚀"
            )
            st.toast(
                f"Order placed by "
                f"{st.session_state.submitted_by} ⚡"
            )
            st.session_state.submitted = False
            st.session_state.submitted_by = ""
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.write(
                f"**👤 User:** "
                f"{st.session_state.user_name}"
            )
        with col2:
            st.write(
                f"**🔑 Role:** "
                f"{st.session_state.role}"
            )
        st.subheader("🏪 Select Party")
        if not st.session_state.user_parties:
            st.error(
                "Is user ke saath koi party mapped nahi hai ❌"
            )
            st.stop()
        v = st.session_state.form_version
        party_list = (
            ["-- Select Party --"]
            + st.session_state.user_parties
        )
        party_option = st.selectbox(
            "Party",
            party_list,
            key=f"party_{v}"
        )
        party = (
            party_option
            if party_option != "-- Select Party --"
            else None
        )
        st.subheader("➕ Add Item")
        col1, col2 = st.columns(2)
        with col1:
            try:
                df = get_cached("cached_stock_df", load_stock)
                if "SKU" not in df.columns:
                    st.error(
                        "Stock sheet mein SKU column nahi mila ❌"
                    )
                    st.stop()
                sku_list = (
                    ["-- Select SKU --"]
                    + df["SKU"]
                    .dropna()
                    .astype(str)
                    .str.strip()
                    .tolist()
                )
                sku = st.selectbox(
                    "Select SKU",
                    sku_list,
                    key=f"sku_{v}"
                )
                if (
                    st.session_state.last_sku
                    != sku
                ):
                    st.session_state[
                        f"qty_{v}"
                    ] = 1
                    st.session_state.last_sku = sku
            except Exception as e:
                st.error(
                    f"Stock load error: {e}"
                )
                st.stop()
        with col2:
            qty = st.number_input(
                "Quantity",
                min_value=1,
                step=1,
                key=f"qty_{v}"
            )
        if st.button(
            "➕ Add to Cart",
            use_container_width=True
        ):
            if sku == "-- Select SKU --":
                st.warning(
                    "Pehle ek valid SKU select karo ❌"
                )
            else:
                found = False
                for item in st.session_state.cart:
                    if item["SKU"] == sku:
                        item["QTY"] += qty
                        found = True
                        break
                if not found:
                    st.session_state.cart.append(
                        {
                            "SKU": sku,
                            "QTY": qty
                        }
                    )
                st.success(
                    "Item Added ✅"
                )
        st.subheader(
            "🧾 Your Order"
        )
        if st.session_state.cart:
            for i, item in enumerate(
                st.session_state.cart
            ):
                col1, col2, col3 = st.columns(
                    [5, 2, 1]
                )
                with col1:
                    st.write(
                        f"**SKU:** {item['SKU']}"
                    )
                with col2:
                    st.write(
                        f"**QTY:** {item['QTY']}"
                    )
                with col3:
                    if st.button(
                        "❌",
                        key=f"remove_{i}_{v}"
                    ):
                        st.session_state.cart.pop(i)
                        st.rerun()
            total_qty = sum(
                item["QTY"]
                for item in st.session_state.cart
            )
            st.info(
                f"Total Quantity: {total_qty}"
            )
        else:
            st.warning(
                "Abhi koi item add nahi hua ❌"
            )
        if st.session_state.cart:
            if st.button(
                "🗑 Clear Cart",
                use_container_width=True
            ):
                st.session_state.cart = []
                st.session_state.last_sku = None
                st.rerun()
        st.divider()
        if st.button(
            "✅ Submit Order",
            use_container_width=True
        ):
            if not party:
                st.warning(
                    "Party select karo ❌"
                )
            elif not st.session_state.cart:
                st.warning(
                    "Cart khali hai ❌"
                )
            else:
                invalid_skus = [
                    item["SKU"]
                    for item in st.session_state.cart
                    if item["SKU"]
                    == "-- Select SKU --"
                ]
                if invalid_skus:
                    st.warning(
                        "Cart mein invalid SKU hai. "
                        "Pehle remove karo ❌"
                    )
                else:
                    payload = []
                    for item in st.session_state.cart:
                        payload.append(
                            {
                                "date": date_time,
                                "user": (
                                    st.session_state.user_name
                                ),
                                "party": party,
                                "sku": str(
                                    item["SKU"]
                                ),
                                "qty": int(
                                    item["QTY"]
                                )
                            }
                        )
                    # ==================================================
                    # CREATE ORDER → EXISTING CREATE ORDER API
                    # ==================================================
                    threading.Thread(
                        target=send_data,
                        args=(payload,),
                        daemon=True
                    ).start()
                    st.session_state.cart = []
                    st.session_state.last_sku = None
                    st.session_state.submitted = True
                    st.session_state.submitted_by = (
                        st.session_state.user_name
                    )
                    st.session_state.form_version += 1
                    st.rerun()
    # ========================================================
    # ORDER ACTIVITY
    # ========================================================
    elif st.session_state.page == "Order Activity":
        st.title(
            "📋 Order Activity"
        )
        st.caption(
            f"Showing orders for mapped parties of "
            f"{st.session_state.user_name}"
        )
        st.divider()
        is_admin = (
            st.session_state.role.strip().upper()
            == "ADMIN"
        )
        if (
            not is_admin
            and not st.session_state.user_parties
        ):
            st.error(
                "Is user ke saath koi party mapped nahi hai ❌"
            )
            st.stop()
        with st.spinner(
            "Loading order activity..."
        ):
            oa_parties_key = (
                ()
                if is_admin
                else tuple(
                    st.session_state.user_parties
                )
            )
            result = get_cached(
                f"cached_order_activity_{is_admin}_{oa_parties_key}",
                get_order_activity,
                oa_parties_key
            )
        if not result.get("success"):
            st.error(
                result.get(
                    "message",
                    "Order Activity load nahi ho paayi ❌"
                )
            )
            st.stop()
        order_data = result.get(
            "data",
            []
        )
        if not order_data:
            st.info(
                "Order Sheet mein abhi koi order data nahi hai."
            )
            st.stop()
        activity_df = pd.DataFrame(
            order_data
        )
        activity_df.columns = (
            activity_df.columns
            .astype(str)
            .str.strip()
            .str.upper()
        )
        required_columns = [
            "DATE",
            "PARTY",
            "SKU",
            "QTY",
            "FINAL STATUS"
        ]
        missing_columns = [
            col
            for col in required_columns
            if col not in activity_df.columns
        ]
        if missing_columns:
            st.error(
                "ORDER SHEET mein required columns nahi mile: "
                + ", ".join(missing_columns)
            )
            st.stop()
        activity_df["PARTY"] = (
            activity_df["PARTY"]
            .fillna("")
            .astype(str)
            .str.strip()
        )
        mapped_parties = [
            str(p).strip()
            for p in st.session_state.user_parties
        ]
        if not is_admin:
            activity_df = activity_df[
                activity_df["PARTY"].isin(
                    mapped_parties
                )
            ].copy()
        if (
            is_admin
            and "USER" in activity_df.columns
        ):
            activity_df["USER"] = (
                activity_df["USER"]
                .fillna("")
                .astype(str)
                .str.strip()
            )
            user_filter_options = (
                ["All Users"]
                + sorted(
                    [
                        u
                        for u in activity_df["USER"].unique()
                        if u
                    ]
                )
            )
            selected_user_filter = st.selectbox(
                "👤 Filter by User",
                user_filter_options,
                key="admin_order_user_filter"
            )
            if (
                selected_user_filter
                != "All Users"
            ):
                activity_df = activity_df[
                    activity_df["USER"]
                    == selected_user_filter
                ].copy()
        activity_df["DATE_RAW"] = (
            activity_df["DATE"]
            .fillna("")
            .astype(str)
            .str.strip()
        )
        parsed_dates = pd.to_datetime(
            activity_df["DATE_RAW"],
            errors="coerce",
            dayfirst=True
        )
        activity_df["ORDER_DATE_ONLY"] = (
            parsed_dates.dt.date
        )
        activity_df["FINAL STATUS"] = (
            activity_df["FINAL STATUS"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.upper()
        )
        billed_statuses = [
            "PUNCHED IN L1",
            "PUNCHED IN L3"
        ]
        cancelled_statuses = [
            "CANCELLED"
        ]
        activity_df["ACTIVITY STATUS"] = (
            "Pending"
        )
        activity_df.loc[
            activity_df["FINAL STATUS"].isin(
                billed_statuses
            ),
            "ACTIVITY STATUS"
        ] = "Billed"
        activity_df.loc[
            activity_df["FINAL STATUS"].isin(
                cancelled_statuses
            ),
            "ACTIVITY STATUS"
        ] = "Cancelled"
        billed_tab, pending_tab, cancelled_tab = st.tabs(
            [
                "✅ Billed",
                "⏳ Pending",
                "❌ Cancelled"
            ]
        )
        # ====================================================
        # BILLED
        # ====================================================
        with billed_tab:
            st.subheader(
                "✅ Billed Orders"
            )
            col1, col2 = st.columns(
                [5, 1]
            )
            with col1:
                billed_date_input = st.date_input(
                    "Billed Order Date",
                    value=now_ist.date(),
                    key="billed_date_input"
                )
            with col2:
                st.write("")
                billed_submit = st.button(
                    "🔍 Submit",
                    key="billed_submit",
                    use_container_width=True
                )
            if billed_submit:
                st.session_state.billed_date = (
                    billed_date_input
                )
            billed_df = activity_df[
                activity_df["ACTIVITY STATUS"]
                == "Billed"
            ].copy()
            if (
                st.session_state.billed_date
                is not None
            ):
                billed_df = billed_df[
                    billed_df["ORDER_DATE_ONLY"]
                    == st.session_state.billed_date
                ].copy()
            st.metric(
                "✅ Billed Orders",
                len(billed_df)
            )
            if billed_df.empty:
                st.info(
                    "Koi Billed order nahi mila."
                )
            else:
                display_columns = [
                    "DATE",
                    "USER",
                    "PARTY",
                    "SKU",
                    "QTY",
                    "FINAL STATUS"
                ] if is_admin else [
                    "DATE",
                    "PARTY",
                    "SKU",
                    "QTY",
                    "FINAL STATUS"
                ]
                available_columns = [
                    col
                    for col in display_columns
                    if col in billed_df.columns
                ]
                st.dataframe(
                    billed_df[
                        available_columns
                    ],
                    use_container_width=True,
                    hide_index=True
                )
        # ====================================================
        # PENDING
        # ====================================================
        with pending_tab:
            st.subheader(
                "⏳ Pending Orders"
            )
            col1, col2 = st.columns(
                [5, 1]
            )
            with col1:
                pending_date_input = st.date_input(
                    "Pending Order Date",
                    value=now_ist.date(),
                    key="pending_date_input"
                )
            with col2:
                st.write("")
                pending_submit = st.button(
                    "🔍 Submit",
                    key="pending_submit",
                    use_container_width=True
                )
            if pending_submit:
                st.session_state.pending_date = (
                    pending_date_input
                )
            pending_df = activity_df[
                activity_df["ACTIVITY STATUS"]
                == "Pending"
            ].copy()
            if (
                st.session_state.pending_date
                is not None
            ):
                pending_df = pending_df[
                    pending_df["ORDER_DATE_ONLY"]
                    == st.session_state.pending_date
                ].copy()
            st.metric(
                "⏳ Pending Orders",
                len(pending_df)
            )
            if pending_df.empty:
                st.success(
                    "Koi Pending order nahi mila 🎉"
                )
            else:
                display_columns = [
                    "DATE",
                    "USER",
                    "PARTY",
                    "SKU",
                    "QTY",
                    "FINAL STATUS"
                ] if is_admin else [
                    "DATE",
                    "PARTY",
                    "SKU",
                    "QTY",
                    "FINAL STATUS"
                ]
                available_columns = [
                    col
                    for col in display_columns
                    if col in pending_df.columns
                ]
                st.dataframe(
                    pending_df[
                        available_columns
                    ],
                    use_container_width=True,
                    hide_index=True
                )
        # ====================================================
        # CANCELLED
        # ====================================================
        with cancelled_tab:
            st.subheader(
                "❌ Cancelled Orders"
            )
            col1, col2 = st.columns(
                [5, 1]
            )
            with col1:
                cancelled_date_input = st.date_input(
                    "Cancelled Order Date",
                    value=now_ist.date(),
                    key="cancelled_date_input"
                )
            with col2:
                st.write("")
                cancelled_submit = st.button(
                    "🔍 Submit",
                    key="cancelled_submit",
                    use_container_width=True
                )
            if cancelled_submit:
                st.session_state.cancelled_date = (
                    cancelled_date_input
                )
            cancelled_df = activity_df[
                activity_df["ACTIVITY STATUS"]
                == "Cancelled"
            ].copy()
            if (
                st.session_state.cancelled_date
                is not None
            ):
                cancelled_df = cancelled_df[
                    cancelled_df["ORDER_DATE_ONLY"]
                    == st.session_state.cancelled_date
                ].copy()
            st.metric(
                "❌ Cancelled Orders",
                len(cancelled_df)
            )
            if cancelled_df.empty:
                st.info(
                    "Koi Cancelled order nahi mila."
                )
            else:
                display_columns = [
                    "DATE",
                    "USER",
                    "PARTY",
                    "SKU",
                    "QTY",
                    "FINAL STATUS"
                ] if is_admin else [
                    "DATE",
                    "PARTY",
                    "SKU",
                    "QTY",
                    "FINAL STATUS"
                ]
                available_columns = [
                    col
                    for col in display_columns
                    if col in cancelled_df.columns
                ]
                st.dataframe(
                    cancelled_df[
                        available_columns
                    ],
                    use_container_width=True,
                    hide_index=True
                )
    # ========================================================
    # STOCK
    # ========================================================
    elif st.session_state.page == "Stock":
        st.title("📊 Stock")
        st.caption(
            "Live stock information"
        )
        st.divider()
        try:
            stock_df = get_cached("cached_stock_df", load_stock)
        except Exception as e:
            st.error(
                f"Stock load error: {e}"
            )
            st.stop()
        if stock_df.empty:
            st.warning(
                "Stock sheet mein koi data nahi mila."
            )
            st.stop()
        if "PRODUCT NAME" in stock_df.columns:
            product_names = (
                stock_df["PRODUCT NAME"]
                .fillna("")
                .astype(str)
                .str.strip()
            )
            product_names = sorted(
                [
                    x
                    for x in product_names.unique()
                    if x
                ]
            )
            filter_options = [
                "All Products"
            ] + product_names
            selected_product = st.selectbox(
                "🔎 Product Name",
                filter_options,
                key="stock_product_filter"
            )
            if selected_product != "All Products":
                filtered_stock_df = stock_df[
                    stock_df["PRODUCT NAME"]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                    == selected_product
                ].copy()
            else:
                filtered_stock_df = stock_df.copy()
        else:
            st.warning(
                "Stock sheet mein PRODUCT NAME column nahi mila."
            )
            filtered_stock_df = stock_df.copy()
        stock_display_df = (
            filtered_stock_df.copy()
        )
        if (
            "SKU" in stock_display_df.columns
            and "SKU CODE" in stock_display_df.columns
        ):
            stock_display_df = (
                stock_display_df.drop(
                    columns=["SKU"]
                )
            )
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "📦 Total Products",
                len(stock_display_df)
            )
        with col2:
            st.metric(
                "📋 Total Columns",
                len(stock_display_df.columns)
            )
        st.divider()
        stock_kpi_cols = [
            "FARUKHNAGAR",
            "MUMBAI STOCK"
        ]
        l3_matching_cols = [
            col
            for col in filtered_stock_df.columns
            if "L3" in col
        ]
        l3_actual_col = (
            l3_matching_cols[0]
            if l3_matching_cols
            else None
        )
        available_kpi_cols = [
            col
            for col in stock_kpi_cols
            if col in filtered_stock_df.columns
        ]
        if l3_actual_col:
            available_kpi_cols.append(l3_actual_col)
        if available_kpi_cols:
            kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
            kpi_targets = {
                "FARUKHNAGAR": (
                    kpi_col1,
                    "🏭 Farukhnagar Stock"
                ),
                "MUMBAI STOCK": (
                    kpi_col2,
                    "🏙 Mumbai Stock"
                )
            }
            if l3_actual_col:
                kpi_targets[l3_actual_col] = (
                    kpi_col3,
                    "🇮🇳 L3 Stock (PAN India)"
                )
            for kpi_col_name, (kpi_slot, kpi_label) in kpi_targets.items():
                with kpi_slot:
                    if kpi_col_name in filtered_stock_df.columns:
                        kpi_values = pd.to_numeric(
                            filtered_stock_df[kpi_col_name]
                            .astype(str)
                            .str.replace(",", "", regex=False)
                            .str.strip(),
                            errors="coerce"
                        ).fillna(0)
                        st.metric(
                            kpi_label,
                            int(kpi_values.sum())
                        )
                    else:
                        st.metric(
                            kpi_label,
                            "N/A"
                        )
            st.divider()
        csv_data = (
            stock_display_df
            .to_csv(index=False)
            .encode("utf-8")
        )
        st.download_button(
            label="⬇️ Download Stock",
            data=csv_data,
            file_name="stock_data.csv",
            mime="text/csv",
            use_container_width=True
        )
        st.divider()
        st.subheader(
            "📦 Stock Details"
        )
        st.dataframe(
            stock_display_df,
            use_container_width=True,
            hide_index=True
        )
    # ========================================================
    # OD STATUS
    # ========================================================
    elif st.session_state.page == "OD Status":
        st.title("💰 OD Status")
        st.caption(
            f"Outstanding for mapped parties of "
            f"{st.session_state.user_name}"
        )
        st.divider()
        is_admin = (
            st.session_state.role.strip().upper()
            == "ADMIN"
        )
        if (
            not is_admin
            and not st.session_state.user_parties
        ):
            st.error(
                "Is user ke saath koi party mapped nahi hai ❌"
            )
            st.stop()
        with st.spinner(
            "Loading OD / Outstanding data..."
        ):
            try:
                od_df = get_cached("cached_od_df", load_od_status)
            except Exception as e:
                st.error(
                    f"OD data load error: {e}"
                )
                st.info(
                    "Agar HTTP 401 Unauthorized aa raha hai, "
                    "OD Google Sheet mein "
                    "Share → General Access → "
                    "Anyone with the link → Viewer "
                    "enable karo."
                )
                st.stop()
        if od_df.empty:
            st.info(
                "OD sheet mein koi party data nahi mila."
            )
            st.stop()
        mapped_parties = [
            str(p)
            .strip()
            .upper()
            for p in st.session_state.user_parties
        ]
        od_df["_PARTY_MATCH"] = (
            od_df["PARTY NAME"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.upper()
        )
        if not is_admin:
            od_df = od_df[
                od_df["_PARTY_MATCH"].isin(
                    mapped_parties
                )
            ].copy()
        od_df.drop(
            columns=["_PARTY_MATCH"],
            inplace=True
        )
        if od_df.empty:
            st.warning(
                "Aapki mapped parties ke liye "
                "koi OD data nahi mila."
            )
            st.stop()
        numeric_columns = [
            "OD",
            "OFL",
            "NOT DUE",
            "GRAND TOTAL",
            "CREDIT LIMIT",
            "BALANCE LIMIT"
        ]
        for col in numeric_columns:
            od_df[col] = pd.to_numeric(
                od_df[col]
                .astype(str)
                .str.replace(
                    ",",
                    "",
                    regex=False
                )
                .str.replace(
                    "₹",
                    "",
                    regex=False
                )
                .str.strip(),
                errors="coerce"
            ).fillna(0)
        total_od = od_df["OD"].sum()
        total_not_due = od_df["NOT DUE"].sum()
        total_grand = od_df["GRAND TOTAL"].sum()
        total_credit_limit = (
            od_df["CREDIT LIMIT"].sum()
        )
        total_balance_limit = (
            od_df["BALANCE LIMIT"].sum()
        )
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "💰 Total OD",
                f"₹{total_od:,.0f}"
            )
        with col2:
            st.metric(
                "📅 Not Due",
                f"₹{total_not_due:,.0f}"
            )
        with col3:
            st.metric(
                "📊 Grand Total",
                f"₹{total_grand:,.0f}"
            )
        with col4:
            st.metric(
                "💳 Credit Limit",
                f"₹{total_credit_limit:,.0f}"
            )
        st.divider()
        st.subheader(
            "💳 Available Balance Limit"
        )
        st.metric(
            "Total Balance Limit",
            f"₹{total_balance_limit:,.0f}"
        )
        st.divider()
        st.subheader(
            "🏪 Party-wise Outstanding"
        )
        st.caption(
            "Sirf aapki mapped parties ka data dikhaya ja raha hai."
        )
        display_columns = [
            "PARTY NAME",
            "OD",
            "OFL",
            "NOT DUE",
            "GRAND TOTAL",
            "CREDIT LIMIT",
            "ZONE",
            "BALANCE LIMIT"
        ]
        display_df = od_df[
            display_columns
        ].copy()
        money_columns = [
            "OD",
            "OFL",
            "NOT DUE",
            "GRAND TOTAL",
            "CREDIT LIMIT",
            "BALANCE LIMIT"
        ]
        for col in money_columns:
            display_df[col] = (
                display_df[col]
                .apply(
                    lambda x:
                    f"₹{x:,.0f}"
                )
            )
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        download_df = od_df[
            display_columns
        ].copy()
        csv_data = (
            download_df
            .to_csv(index=False)
            .encode("utf-8")
        )
        st.download_button(
            label="⬇️ Download OD Report",
            data=csv_data,
            file_name="party_wise_od_report.csv",
            mime="text/csv",
            use_container_width=True
        )
    # ========================================================
    # SKU PHOTO
    # ========================================================
    elif st.session_state.page == "SKU Photo":
        st.title("📸 SKU Photo")
        st.caption(
            "SKU select karo aur uski photo(s) dekho"
        )
        st.divider()
        try:
            photo_df = load_sku_photos()
        except Exception as e:
            st.error(
                f"Photo data load error: {e}"
            )
            st.stop()
        if photo_df.empty:
            st.warning(
                "Photo sheet mein koi data nahi mila."
            )
            st.stop()
        if (
            "SKU CODE" not in photo_df.columns
            or "IMAGE URL" not in photo_df.columns
        ):
            st.error(
                "Photo sheet mein SKU CODE ya IMAGE URL column nahi mila ❌"
            )
            st.stop()
        if "PRODUCT NAME" not in photo_df.columns:
            st.error(
                "Photo sheet mein PRODUCT NAME column nahi mila ❌"
            )
            st.stop()
        product_options = sorted(
            [
                x
                for x in photo_df["PRODUCT NAME"]
                .fillna("")
                .astype(str)
                .str.strip()
                .unique()
                if x
            ]
        )
        if not product_options:
            st.info(
                "Photo sheet mein koi Product nahi mila."
            )
            st.stop()
        selected_product_photo = st.selectbox(
            "🔎 Select Product",
            ["-- Select Product --"]
            + product_options,
            key="product_photo_select"
        )
        st.divider()
        if (
            selected_product_photo
            == "-- Select Product --"
        ):
            st.info(
                "Photo dekhne ke liye upar se Product select karo."
            )
        else:
            matched_rows = photo_df[
                photo_df["PRODUCT NAME"]
                .fillna("")
                .astype(str)
                .str.strip()
                == selected_product_photo
            ].copy()
            # ----------------------------------------------------
            # FIX: build (url, sku_label) pairs together from the
            # same row so nothing drifts out of sync when some
            # rows have an empty IMAGE URL.
            # ----------------------------------------------------
            photo_pairs = []
            for _, row in matched_rows.iterrows():
                row_url = str(row.get("IMAGE URL", "")).strip()
                if row_url:
                    row_sku_label = str(row.get("SKU CODE", "")).strip()
                    photo_pairs.append((row_url, row_sku_label))
            if not photo_pairs:
                st.warning(
                    "Is Product ke liye koi photo nahi mili ❌"
                )
            else:
                st.subheader(
                    f"🏷 {selected_product_photo}"
                )
                st.caption(
                    f"{len(photo_pairs)} photo(s) mili"
                )
                cols = st.columns(3)
                for idx, (url, sku_label) in enumerate(photo_pairs):
                    with cols[idx % 3]:
                        try:
                            st.image(
                                url,
                                use_container_width=True,
                                caption=(
                                    sku_label
                                    if sku_label
                                    else None
                                )
                            )
                        except Exception:
                            st.warning(
                                "Ye image load nahi ho payi ❌"
                            )
