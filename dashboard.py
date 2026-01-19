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
    
    # Expandable Checkbox Filters
    with st.expander("🏢 Hiring Manager", expanded=False):
        hm_options = sorted(df_raw['HM Details'].dropna().unique())
        hm_filter = [hm for hm in hm_options if st.checkbox(hm, key=f"hm_{hm}")]
    
    with st.expander("💼 Skill", expanded=False):
        skill_options = sorted(df_raw['Skill'].dropna().unique())
        skill_filter = [skill for skill in skill_options if st.checkbox(skill, key=f"skill_{skill}")]
    
    with st.expander("📍 Location", expanded=False):
        loc_options = sorted(df_raw['Location of posting'].dropna().unique())
        loc_filter = [loc for loc in loc_options if st.checkbox(loc, key=f"loc_{loc}")]
    
    with st.expander("👤 Recruiter", expanded=False):
        recruiter_options = sorted(df_raw['Recruiter Name'].dropna().unique())
        recruiter_filter = [recruiter for recruiter in recruiter_options if st.checkbox(recruiter, key=f"recruiter_{recruiter}")]
    
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

# 4. Funnel Chart - Recruitment Pipeline
st.subheader("Recruitment Pipeline Funnel")

# Calculate funnel metrics
total_candidates = len(df)
screening_rejected = len(df[df['Dashboard_Category'] == 'Screening Reject'])
interview_rejected = len(df[df['Dashboard_Category'] == 'Rejected'])
shortlisted = len(df[df['Dashboard_Category'] == 'Pending/Active'])
selected = len(df[df['Dashboard_Category'] == 'Selected'])

# Create funnel data (Total at top, Selected at bottom, left-aligned)
funnel_data = {
    'Stage': ['Total Candidates', 'After Screening', 'After Interviews', 'Shortlisted', 'Selected'],
    'Count': [total_candidates, total_candidates - screening_rejected, total_candidates - screening_rejected - interview_rejected, shortlisted, selected]
}
funnel_df = pd.DataFrame(funnel_data)

# Create left-aligned funnel chart using horizontal bar
fig_funnel = px.bar(
    funnel_df,
    y='Stage',
    x='Count',
    orientation='h',
    color='Stage',
    color_discrete_sequence=['#66BB6A', '#1976D2', '#FF6F00', '#FFC107', '#5C6BC0'],
    text='Count'
)
fig_funnel.update_layout(
    height=400,
    showlegend=False,
    xaxis_title="Number of Candidates",
    yaxis_title=None,
    xaxis=dict(showgrid=True),
    yaxis=dict(categoryorder='array', categoryarray=['Selected', 'Shortlisted', 'After Interviews', 'After Screening', 'Total Candidates']),
)
fig_funnel.update_traces(textposition='outside')
st.plotly_chart(fig_funnel, use_container_width=True)

# Display Pending candidates info below funnel
pending_info = f"**Pending/Active Candidates:** {len(df[df['Dashboard_Category'] == 'Pending/Active'])} candidates currently in the pipeline"
st.info(pending_info)

# 5. Candidate-Specific KPIs
st.subheader("Candidate Metrics")

# Prepare KPI data for candidates
kpi_columns = ['Candidate Name', 'HM Details', 'Skill', 'Status', 'Dashboard_Category', 'TTF (60 days)', 'TTH (30 days)']
df_kpi = df[kpi_columns].copy()
df_kpi.columns = ['Candidate Name', 'HM', 'Skill', 'Status', 'Category', 'TTF', 'TTH']

# Rename columns for display and convert to numeric where possible
df_kpi_display = df_kpi.copy()
df_kpi_display['TTF'] = pd.to_numeric(df_kpi_display['TTF'], errors='coerce')
df_kpi_display['TTH'] = pd.to_numeric(df_kpi_display['TTH'], errors='coerce')

# Calculate Quality of Hire (based on joining status)
def quality_of_hire(row):
    if row['Category'] == 'Selected':
        return 'High'
    elif row['Category'] == 'Pending/Active':
        return 'In Progress'
    else:
        return 'Not Selected'

df_kpi_display['Quality of Hire'] = df_kpi_display.apply(quality_of_hire, axis=1)

# Display as a formatted dataframe
st.dataframe(
    df_kpi_display[['Candidate Name', 'HM', 'Skill', 'TTF', 'TTH', 'Quality of Hire']],
    use_container_width=True,
    height=400
)

# Data Table for deeper look
st.subheader("Full Candidate Details")
st.dataframe(
    df[['Candidate Name', 'HM Details', 'Skill', 'Status', 'Dashboard_Category', 'Recruiter Name']],
    width="stretch",
)