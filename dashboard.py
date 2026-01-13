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
            df[col] = df[col].astype(str).str.strip()

    # Convert Date
    df['Sourcing Date'] = pd.to_datetime(df['Sourcing Date'], errors='coerce')

    # Define Grouping Logic
    selected_list = ['selected', 'Joined', 'Internship letter shared', 'Yes']
    rejected_list = ['Rejected', 'Rejected in R1', 'Rejected in R2', 'Rejected in technical screening', 'Offer Declined...']
    screening_list = ['Screening reject']
    pending_list = ['In process', 'Under discussion', 'Shortlisted', 'Pending at R1', 'Pending at R2', 'Pending at R3', 'on hold', 'Scheduled for R1', 'Scheduled for R2', 'Scheduled for R3']

    def categorize_status(row):
        status = row['Status']
        r1, r2, r3 = row.get('Status of R1'), row.get('Status of R2'), row.get('Status of R3')
        
        if status in selected_list: return 'Selected'
        if status in screening_list: return 'Screening Reject'
        
        if status in rejected_list or 'Rejected' in str(status):
            if pd.isna(r1) and pd.isna(r2) and pd.isna(r3):
                return 'Screening Reject'
            elif r1 == 'Not Cleared': return 'R1 Reject'
            elif r2 == 'Not Cleared': return 'R2 Reject'
            elif r3 == 'Not Cleared': return 'R3 Reject'
            return 'Other Reject'
            
        if any(p in str(status) for p in pending_list): return 'Pending/Active'
        return 'Other'

    df['Dashboard_Category'] = df.apply(categorize_status, axis=1)
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

# Apply Filters
df = df_raw.copy()
if len(date_range) == 2:
    df = df[(df['Sourcing Date'].dt.date >= date_range[0]) & (df['Sourcing Date'].dt.date <= date_range[1])]
if hm_filter: df = df[df['HM Details'].isin(hm_filter)]
if skill_filter: df = df[df['Skill'].isin(skill_filter)]
if loc_filter: df = df[df['Location of posting'].isin(loc_filter)]
if recruiter_filter: df = df[df['Recruiter Name'].isin(recruiter_filter)]
if name_search: df = df[df['Candidate Name'].str.contains(name_search, case=False)]

# 4. Main Dashboard UI
st.title("Candidate Clearance Overview")

# Top Metrics Row with Colored Blocks (Like your reference image)
m1, m2, m3, m4 = st.columns(4)

# Data for blocks
total_val = len(df)
selected_val = len(df[df['Dashboard_Category'] == 'Selected'])
rejected_val = len(df[df['Dashboard_Category'].str.contains('Reject')])
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
    hm_data = df.groupby(['HM Details', 'Dashboard_Category']).size().reset_index(name='Count')
    
    # Using specific blue shades for different categories
    fig_hm = px.bar(hm_data, x='Count', y='HM Details', color='Dashboard_Category',
                   orientation='h', 
                   color_discrete_map={
                       'Selected': '#1A5276',        # Dark Blue
                       'Pending/Active': '#3498DB',  # Bright Blue
                       'Screening Reject': '#85C1E9',# Light Blue
                       'R1 Reject': '#AED6F1',       # Very Light Blue
                       'R2 Reject': '#D6EAF8'        # Faded Blue
                   })
    st.plotly_chart(fig_hm, use_container_width=True)

with col_right:
    st.subheader("Rejection by Round")
    reject_df = df[df['Dashboard_Category'].str.contains('Reject')]
    
    # Pie chart using the blue sequential palette
    fig_reject = px.pie(reject_df, names='Dashboard_Category', hole=0.4,
                       color_discrete_sequence=px.colors.sequential.Blues_r)
    st.plotly_chart(fig_reject, use_container_width=True)

# Data Table for deeper look
st.subheader("Candidate Details")
st.dataframe(df[['Candidate Name', 'HM Details', 'Skill', 'Status', 'Dashboard_Category', 'Recruiter Name']], use_container_width=True)