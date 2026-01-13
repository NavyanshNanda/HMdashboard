import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Candidate Clearance Dashboard", layout="wide")

# Custom CSS to mimic the "ElaAdmin" look (Rounded cards, shadows, dark sidebar)
st.markdown("""
    <style>
    .stApp { background-color: #F0F2F5; }
    [data-testid="stSidebar"] { background-color: #27333E; }
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e6e9ef;
    }
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

# Top Metrics Row
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Candidates", len(df))
m2.metric("Selected", len(df[df['Dashboard_Category'] == 'Selected']))
m3.metric("Rejections (All)", len(df[df['Dashboard_Category'].str.contains('Reject')]))
m4.metric("Pending", len(df[df['Dashboard_Category'] == 'Pending/Active']))

st.divider()

# Charts Row
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("HM Performance Breakdown")
    chart_type = st.radio("View as:", ["Stacked Bar", "Grouped Bar"], horizontal=True)
    
    hm_data = df.groupby(['HM Details', 'Dashboard_Category']).size().reset_index(name='Count')
    fig_hm = px.bar(hm_data, x='Count', y='HM Details', color='Dashboard_Category',
                   orientation='h', barmode='stack' if chart_type == "Stacked Bar" else 'group',
                   color_discrete_map={'Selected':'#57D19A', 'Screening Reject':'#FF6B6B', 'R1 Reject':'#FFADAD', 'R2 Reject':'#FFD6A5', 'Pending/Active':'#3BB1F3'})
    st.plotly_chart(fig_hm, use_container_width=True)

with col_right:
    st.subheader("Rejection by Round")
    reject_df = df[df['Dashboard_Category'].str.contains('Reject')]
    fig_reject = px.pie(reject_df, names='Dashboard_Category', hole=0.4,
                       color_discrete_sequence=px.colors.sequential.Reds_r)
    st.plotly_chart(fig_reject, use_container_width=True)

# Data Table for deeper look
st.subheader("Candidate Details")
st.dataframe(df[['Candidate Name', 'HM Details', 'Skill', 'Status', 'Dashboard_Category', 'Recruiter Name']], use_container_width=True)