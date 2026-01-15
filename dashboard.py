import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Candidate Clearance Dashboard", layout="wide")

# Custom CSS to mimic the "ElaAdmin" look (Rounded cards, shadows, dark sidebar)
# Updated CSS for Colored KPI Blocks and Black Text
st.markdown("""
    <style>
    /* Main background */
    .stApp { background-color: #f4f7f6 !important; }

    /* Force all standard text to Black */
    h1, h2, h3, p, span, label {
        color: #000000 !important;
    }

    /* Sidebar text fix (keep it light against the dark background) */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {
        color: #ffffff !important;
    }

    /* Custom KPI Card Styling */
    .kpi-card {
        padding: 20px;
        border-radius: 10px;
        color: white !important;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .kpi-card h3 { color: white !important; margin: 0; font-size: 1rem; }
    .kpi-card h2 { color: white !important; margin: 0; font-size: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# 2. Data Loading & Logic
@st.cache_data(ttl=60)
def load_and_clean_data():
    # Load and skip the first metadata row
    df = pd.read_csv('TA Tracker - HM Sheet.csv', skiprows=1)
    df.columns = [col.strip() for col in df.columns]
    
    # Clean string columns
    str_cols = ['Status', 'HM Details', 'Skill', 'Location of posting', 'Recruiter Name', 'Candidate Name']
    for col in str_cols:
        if col in df.columns:
            # Use pandas "string" dtype so missing values stay as <NA> (not the literal "nan")
            df[col] = df[col].astype("string").str.strip()

    # Convert Date
    df['Sourcing Date'] = pd.to_datetime(df['Sourcing Date'], errors='coerce')

    # Define Grouping Logic
    selected_list = {'selected', 'joined', 'internship letter shared', 'yes'}
    rejected_list = {'rejected', 'rejected in r1', 'rejected in r2', 'rejected in technical screening', 'offer declined...'}
    screening_list = {'screening reject'}
    pending_list = {
        'in process', 'under discussion', 'shortlisted',
        'pending at r1', 'pending at r2', 'pending at r3',
        'on hold',
        'scheduled for r1', 'scheduled for r2', 'scheduled for r3',
    }

    def categorize_status(row):
        status = row.get('Status')
        r1, r2, r3 = row.get('Status of R1'), row.get('Status of R2'), row.get('Status of R3')

        # Normalize text safely
        status_txt = "" if pd.isna(status) else str(status).strip()
        status_lc = status_txt.lower()
        r1_txt = "" if pd.isna(r1) else str(r1).strip()
        r2_txt = "" if pd.isna(r2) else str(r2).strip()
        r3_txt = "" if pd.isna(r3) else str(r3).strip()
        
        # Treat blanks as Pending (requested)
        if status_txt == "" or status_lc == "nan":
            return ('Pending/Active', None)

        if status_lc in selected_list:
            return ('Selected', None)
        if status_lc in screening_list:
            return ('Screening Reject', None)
        
        # Determine reject round (but we’ll consolidate by default in the charts)
        reject_round = None
        if r1_txt == 'Not Cleared':
            reject_round = 'R1'
        elif r2_txt == 'Not Cleared':
            reject_round = 'R2'
        elif r3_txt == 'Not Cleared':
            reject_round = 'R3'

        if status_lc in rejected_list or ('rejected' in status_lc):
            # If no round info, treat as screening reject (keeps your prior behavior)
            if reject_round is None and (r1_txt == "" and r2_txt == "" and r3_txt == ""):
                return ('Screening Reject', None)
            return ('Rejected', reject_round)
            
        if status_lc in pending_list:
            return ('Pending/Active', None)

        return ('Other', None)

    df[['Dashboard_Category', 'Reject_Round']] = df.apply(categorize_status, axis=1, result_type='expand')
    return df

df_raw = load_and_clean_data()

# 3. Sidebar Filters
with st.sidebar:
    st.title("TA Analytics")
    st.subheader("Filters")
    
    # Date Range Filter
    min_date = df_raw['Sourcing Date'].min()
    max_date = df_raw['Sourcing Date'].max()
    date_range = st.date_input("Sourcing Date Range", [min_date, max_date])
    
    # Select Filters
    hm_filter = st.multiselect("Hiring Manager", options=df_raw['HM Details'].unique())
    skill_filter = st.multiselect("Skill", options=df_raw['Skill'].unique())
    loc_filter = st.multiselect("Location", options=df_raw['Location of posting'].unique())
    recruiter_filter = st.multiselect("Recruiter", options=df_raw['Recruiter Name'].unique())
    name_search = st.text_input("Search Candidate Name")

    # Reject view controls
    reject_view = st.selectbox(
        "Rejects View",
        options=["Combined (default)", "By Round"],
        help="Default combines all rejects into one bucket. 'By Round' breaks rejects into R1/R2/R3.",
    )
    reject_round_filter = st.selectbox(
        "Reject Round (when 'By Round')",
        options=["All", "R1", "R2", "R3"],
        disabled=(reject_view != "By Round"),
    )

# Apply Filters
df = df_raw.copy()
if len(date_range) == 2:
    df = df[(df['Sourcing Date'].dt.date >= date_range[0]) & (df['Sourcing Date'].dt.date <= date_range[1])]
if hm_filter: df = df[df['HM Details'].isin(hm_filter)]
if skill_filter: df = df[df['Skill'].isin(skill_filter)]
if loc_filter: df = df[df['Location of posting'].isin(loc_filter)]
if recruiter_filter: df = df[df['Recruiter Name'].isin(recruiter_filter)]
if name_search: df = df[df['Candidate Name'].str.contains(name_search, case=False)]

# Build a chart-friendly category that consolidates rejects by default
df_chart = df.copy()
if reject_view == "Combined (default)":
    df_chart["Chart_Category"] = df_chart["Dashboard_Category"].where(
        df_chart["Dashboard_Category"] != "Rejected", "Rejected"
    )
else:
    # Break rejects into R1/R2/R3 when possible
    def _chart_category(row):
        if row["Dashboard_Category"] != "Rejected":
            return row["Dashboard_Category"]
        rr = row.get("Reject_Round")
        return f"{rr} Reject" if rr in {"R1", "R2", "R3"} else "Other Reject"

    df_chart["Chart_Category"] = df_chart.apply(_chart_category, axis=1)
    if reject_round_filter != "All":
        # In by-round mode, optionally focus charts on just one round of rejects
        df_chart = df_chart[df_chart["Chart_Category"] == f"{reject_round_filter} Reject"]

# 4. Main Dashboard UI
st.title("Candidate Clearance Overview")

# Top Metrics Row with Colored Blocks (Like your reference image)
m1, m2, m3, m4 = st.columns(4)

# Data for blocks
total_val = len(df)
selected_val = len(df[df['Dashboard_Category'] == 'Selected'])
rejected_val = len(df[df['Dashboard_Category'] == 'Rejected'])
pending_val = len(df[df['Dashboard_Category'] == 'Pending/Active'])

# Rendering Blocks
with m1:
    st.markdown(f"""<div class="kpi-card" style="background-color: #5C6BC0;">
        <h3>Total Candidates</h3><h2>{total_val}</h2>
    </div>""", unsafe_allow_html=True)

with m2:
    st.markdown(f"""<div class="kpi-card" style="background-color: #66BB6A;">
        <h3>Selected</h3><h2>{selected_val}</h2>
    </div>""", unsafe_allow_html=True)

with m3:
    st.markdown(f"""<div class="kpi-card" style="background-color: #EF5350;">
        <h3>Rejections</h3><h2>{rejected_val}</h2>
    </div>""", unsafe_allow_html=True)

with m4:
    st.markdown(f"""<div class="kpi-card" style="background-color: #26C6DA;">
        <h3>Pending</h3><h2>{pending_val}</h2>
    </div>""", unsafe_allow_html=True)

st.divider()

# 4. Charts Row (Updated with Blue Tones)
col_left, col_right = st.columns([2, 1])

# Define a Professional Blue Palette
blue_palette = ['#003f5c', '#2f4b7c', '#665191', '#a05195', '#d45087']

with col_left:
    st.subheader("HM Performance Breakdown")
    hm_data = df_chart.groupby(['HM Details', 'Chart_Category']).size().reset_index(name='Count')

    color_map = {
        "Selected": "#2E7D32",
        "Pending/Active": "#1976D2",
        "Rejected": "#D32F2F",
        "Screening Reject": "#F57C00",
        "R1 Reject": "#C62828",
        "R2 Reject": "#B71C1C",
        "R3 Reject": "#8E0000",
        "Other Reject": "#6D0000",
        "Other": "#6B7280",
    }

    # Cleaner stacked bar view
    fig_hm = px.bar(
        hm_data,
        x="HM Details",
        y="Count",
        color="Chart_Category",
        barmode="stack",
        color_discrete_map=color_map,
    )
    fig_hm.update_layout(xaxis_title=None, yaxis_title="Candidates", legend_title_text=None)
    st.plotly_chart(fig_hm, width="stretch")

with col_right:
    st.subheader("Rejection by Round")
    reject_df = df_chart[df_chart['Chart_Category'].str.contains('Reject', na=False)]

    if len(reject_df) == 0:
        st.info("No rejected candidates in the current selection.")
    else:
        fig_reject = px.pie(
            reject_df,
            names="Chart_Category",
            hole=0.4,
            color="Chart_Category",
            color_discrete_map=color_map,
        )
        fig_reject.update_layout(legend_title_text=None)
        st.plotly_chart(fig_reject, width="stretch")

# Data Table for deeper look
st.subheader("Candidate Details")
st.dataframe(
    df[['Candidate Name', 'HM Details', 'Skill', 'Status', 'Dashboard_Category', 'Recruiter Name']],
    width="stretch",
)