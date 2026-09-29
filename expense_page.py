import streamlit as st
import pandas as pd

# ============================================================
# CONFIG
# ============================================================

# Expense data wali sheet (Sheet1)
EXPENSE_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1draPbcgconYf755uu48q9i-JazkD_vPscMd-sofl55U/"
    "export?format=csv&gid=0"
)

# User -> Zone mapping wali sheet/tab.
# Columns: USERNAME | ZONE   (ek user ke ek se zyada zone ho to alag-alag rows)
# Same file mein nayi tab bana sakte ho, uska gid yahan daalo.
ZONE_MAP_URL = (
"https://docs.google.com/spreadsheets/d/"
    "1draPbcgconYf755uu48q9i-JazkD_vPscMd-sofl55U/"
    "export?format=csv&gid=2123314010"
)

DATE_COL = "DATE"   # jisme May-26, Jun-26 jaisa month hai
ZONE_COL = "ZONE"


# ============================================================
# HELPERS
# ============================================================

def _norm(x):
    return " ".join(str(x).split()).upper()


def _clean_cols(df):
    df.columns = df.columns.astype(str).str.strip().str.upper()
    return df.dropna(how="all").copy()


@st.cache_data(ttl=120)
def load_expense():
    return _clean_cols(pd.read_csv(EXPENSE_URL))


@st.cache_data(ttl=120)
def load_zone_map():
    return _clean_cols(pd.read_csv(ZONE_MAP_URL))


# ============================================================
# PAGE
# ============================================================

def render_expense_page():

    st.title("💸 Expense")
    st.divider()

    is_admin = st.session_state.role.strip().upper() == "ADMIN"

    # ---------------- LOAD ----------------
    try:
        with st.spinner("Loading expense data..."):
            df = load_expense()
    except Exception as e:
        st.error(f"Expense data load error: {e}")
        st.info("Sheet ko Share → Anyone with the link → Viewer karo.")
        st.stop()

    if df.empty:
        st.info("Expense sheet mein koi data nahi mila.")
        st.stop()

    for c in (DATE_COL, ZONE_COL):
        if c not in df.columns:
            st.error(f"Expense sheet mein '{c}' column nahi mila ❌")
            st.write("Sheet ke columns:", list(df.columns))
            st.stop()

    df["_ZONE"] = df[ZONE_COL].apply(_norm)

    # ---------------- ZONE ACCESS ----------------
    if not is_admin:

        try:
            zmap = load_zone_map()
        except Exception as e:
            st.error(f"Zone mapping load error: {e}")
            st.stop()

        if "USERNAME" not in zmap.columns or ZONE_COL not in zmap.columns:
            st.error("Mapping sheet mein USERNAME aur ZONE column chahiye ❌")
            st.write("Mapping sheet ke columns:", list(zmap.columns))
            st.stop()

        my_keys = {
            _norm(st.session_state.username),
            _norm(st.session_state.user_name),
        }

        my_zones = {
            _norm(z)
            for u, z in zip(zmap["USERNAME"], zmap[ZONE_COL])
            if _norm(u) in my_keys
        }

        if not my_zones:
            st.error("Is user ke liye koi zone mapped nahi hai ❌")
            st.stop()

        df = df[df["_ZONE"].isin(my_zones)].copy()

    # ---------------- FILTERS ----------------
    f1, f2 = st.columns(2)

    # Month filter
    with f1:
        raw_months = [
            m for m in df[DATE_COL].fillna("").astype(str).str.strip().unique() if m
        ]
        parsed = {m: pd.to_datetime(m, format="%b-%y", errors="coerce") for m in raw_months}
        months = sorted(
            raw_months,
            key=lambda m: (pd.isna(parsed[m]), parsed[m]),
            reverse=True,   # latest month upar
        )

        month_options = ["All Months"] + months

        selected_month = st.selectbox(
            "📅 Month",
            month_options,
            index=1 if months else 0,   # default: latest month
            key="expense_month_filter",
        )

    if selected_month != "All Months":
        df = df[df[DATE_COL].fillna("").astype(str).str.strip() == selected_month].copy()

    # Zone filter (jab ek se zyada zone dikh rahe ho)
    with f2:
        zones = sorted([z for z in df[ZONE_COL].fillna("").astype(str).str.strip().unique() if z])

        if len(zones) > 1:
            selected_zone = st.selectbox(
                "🌍 Zone",
                ["All Zones"] + zones,
                key="expense_zone_filter",
            )
            if selected_zone != "All Zones":
                df = df[df[ZONE_COL].fillna("").astype(str).str.strip() == selected_zone].copy()

    df = df.drop(columns=["_ZONE"])

    if df.empty:
        st.warning("Is selection ke liye koi data nahi mila.")
        st.stop()

    st.caption(f"{len(df)} rows")

    st.dataframe(df, use_container_width=True, hide_index=True)

    # ---------------- DOWNLOAD ----------------
    month_tag = selected_month.replace(" ", "_")

    st.download_button(
        label="⬇️ Download Expense",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"expense_{month_tag}.csv",
        mime="text/csv",
        use_container_width=True,
    )
