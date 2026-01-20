import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="TA Dashboard - Candidate Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Talent Acquisition Dashboard - Advanced Analytics"
    }
)

# Premium Dashboard CSS Styling
st.markdown("""
    <style>
    /* Force light mode regardless of system preferences */
    :root {
        color-scheme: light !important;
    }
    
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Main App Styling - Light Mode */
    .stApp {
        background: #f8fafc !important;
        font-family: 'Inter', sans-serif;
        color-scheme: light !important;
    }
    
    /* Force all backgrounds to light */
    body {
        background: #f8fafc !important;
        color-scheme: light !important;
    }
    
    /* Main Content Area */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Headers */
    h1 {
        color: #1e293b !important;
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2, h3 {
        color: #334155 !important;
        font-weight: 600 !important;
    }
    
    p {
        color: #64748b !important;
    }
    
    /* Sidebar Styling - Light Theme */
    [data-testid="stSidebar"] {
        background: #ffffff;
        box-shadow: 4px 0 15px rgba(0,0,0,0.05);
    }
    
    [data-testid="stSidebar"] h1 {
        color: #1e293b !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        padding-bottom: 1rem;
        border-bottom: 2px solid #e2e8f0;
    }
    
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] .stMarkdown {
        color: #475569 !important;
    }
    
    /* Expander Styling */
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        background-color: #f1f5f9 !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease;
        color: #334155 !important;
    }
    
    [data-testid="stSidebar"] .streamlit-expanderHeader:hover {
        background-color: #e2e8f0 !important;
        transform: translateX(5px);
    }
    
    /* Checkbox Styling */
    [data-testid="stSidebar"] .stCheckbox {
        padding: 0.25rem 0;
    }
    
    /* Text Input Styling */
    [data-testid="stSidebar"] input[type="text"] {
        border: 2px solid #3b82f6 !important;
        border-radius: 8px !important;
        background: white !important;
        padding: 0.5rem !important;
    }
    
    [data-testid="stSidebar"] input[type="text"]:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Premium KPI Card Styling - Matte Finish */
    .kpi-card {
        padding: 1.5rem;
        border-radius: 12px;
        color: white !important;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: rgba(255,255,255,0.3);
    }
    
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .kpi-card h3 {
        color: rgba(255,255,255,0.95) !important;
        margin: 0 0 0.5rem 0 !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .kpi-card h2 {
        color: white !important;
        margin: 0 !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        line-height: 1;
    }
    
    /* Chart Container Styling */
    .stPlotlyChart {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    /* Dataframe Styling */
    .stDataFrame {
        background: white;
        border-radius: 16px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    /* Info Box Styling */
    .stAlert {
        background: white !important;
        border-radius: 12px !important;
        border-left: 4px solid #3b82f6 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
    }
    
    /* Divider */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: white;
        padding: 0.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        color: #64748b;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #f1f5f9;
        color: #334155;
    }
    
    .stTabs [aria-selected="true"] {
        background: #667eea !important;
        color: white !important;
    }
    
    .stTabs [aria-selected="true"] p {
        color: white !important;
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1rem;
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
            # Use pandas "string" dtype so missing values stay as <NA> (not the literal "nan")
            df[col] = df[col].astype("string").str.strip()

    # Convert Date
    df['Sourcing Date'] = pd.to_datetime(df['Sourcing Date'], errors='coerce')

    # Define Grouping Logic
    joined_list = {'joined', 'internship letter shared'}
    selected_list = {'selected', 'yes', 'shortlisted'}
    rejected_list = {'rejected', 'rejected in r1', 'rejected in r2', 'rejected in technical screening', 'offer declined...'}
    screening_list = {'screening reject'}
    pending_list = {
        'in process', 'under discussion',
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

        if status_lc in joined_list:
            return ('Joined', None)
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
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("✔️ All", key="hm_select_all", use_container_width=True):
                for hm in hm_options:
                    st.session_state[f"hm_{hm}"] = True
        with col_b:
            if st.button("❌ Clear", key="hm_deselect_all", use_container_width=True):
                for hm in hm_options:
                    st.session_state[f"hm_{hm}"] = False
        
        hm_filter = [hm for hm in hm_options if st.checkbox(hm, key=f"hm_{hm}")]
    
    with st.expander("💼 Skill", expanded=False):
        skill_options = sorted(df_raw['Skill'].dropna().unique())
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("✔️ All", key="skill_select_all", use_container_width=True):
                for skill in skill_options:
                    st.session_state[f"skill_{skill}"] = True
        with col_b:
            if st.button("❌ Clear", key="skill_deselect_all", use_container_width=True):
                for skill in skill_options:
                    st.session_state[f"skill_{skill}"] = False
        
        skill_filter = [skill for skill in skill_options if st.checkbox(skill, key=f"skill_{skill}")]
    
    with st.expander("📍 Location", expanded=False):
        loc_options = sorted(df_raw['Location of posting'].dropna().unique())
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("✔️ All", key="loc_select_all", use_container_width=True):
                for loc in loc_options:
                    st.session_state[f"loc_{loc}"] = True
        with col_b:
            if st.button("❌ Clear", key="loc_deselect_all", use_container_width=True):
                for loc in loc_options:
                    st.session_state[f"loc_{loc}"] = False
        
        loc_filter = [loc for loc in loc_options if st.checkbox(loc, key=f"loc_{loc}")]
    
    with st.expander("👤 Recruiter", expanded=False):
        recruiter_options = sorted(df_raw['Recruiter Name'].dropna().unique())
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("✔️ All", key="recruiter_select_all", use_container_width=True):
                for recruiter in recruiter_options:
                    st.session_state[f"recruiter_{recruiter}"] = True
        with col_b:
            if st.button("❌ Clear", key="recruiter_deselect_all", use_container_width=True):
                for recruiter in recruiter_options:
                    st.session_state[f"recruiter_{recruiter}"] = False
        
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
st.markdown("<h1>📊 Talent Acquisition Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748b; font-size: 1.1rem; margin-top: -0.5rem;'>Real-time Candidate Analytics & Insights</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Top Metrics Row with Colored Blocks (Like your reference image)
m1, m2, m3, m4, m5 = st.columns(5)

# Data for blocks
total_val = len(df)
rejected_val = len(df[df['Dashboard_Category'] == 'Rejected'])
selected_val = len(df[df['Dashboard_Category'] == 'Selected'])
joined_val = len(df[df['Dashboard_Category'] == 'Joined'])
pending_val = len(df[df['Dashboard_Category'] == 'Pending/Active'])

# Rendering Blocks (Order: Total, Rejections, Selected, Joined, Pending)
with m1:
    st.markdown(f"""<div class="kpi-card" style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);">
        <h3>👥 Total Candidates</h3><h2>{total_val}</h2>
    </div>""", unsafe_allow_html=True)

with m2:
    st.markdown(f"""<div class="kpi-card" style="background: linear-gradient(135deg, #ec4899 0%, #ef4444 100%);">
        <h3>❌ Rejections</h3><h2>{rejected_val}</h2>
    </div>""", unsafe_allow_html=True)

with m3:
    st.markdown(f"""<div class="kpi-card" style="background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);">
        <h3>⭐ Selected</h3><h2>{selected_val}</h2>
    </div>""", unsafe_allow_html=True)

with m4:
    st.markdown(f"""<div class="kpi-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
        <h3>✅ Joined</h3><h2>{joined_val}</h2>
    </div>""", unsafe_allow_html=True)

with m5:
    st.markdown(f"""<div class="kpi-card" style="background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);">
        <h3>⏳ Pending</h3><h2>{pending_val}</h2>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Analytics Tabs
tab1, tab2, tab3 = st.tabs(["📊 Pipeline Overview", "📈 Candidate Metrics", "📋 Detailed Records"])

# Tab 1: Pipeline Funnel
with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("<h3 style='color: #1e293b; font-weight: 600;'>🎯 Recruitment Pipeline</h3>", unsafe_allow_html=True)
        
        # Calculate funnel metrics
        total_candidates = len(df)
        screening_rejected = len(df[df['Dashboard_Category'] == 'Screening Reject'])
        interview_rejected = len(df[df['Dashboard_Category'] == 'Rejected'])
        shortlisted = len(df[df['Dashboard_Category'] == 'Selected'])
        joined = len(df[df['Dashboard_Category'] == 'Joined'])
        
        # Create funnel data (Total at top, Joined at bottom, left-aligned)
        funnel_data = {
            'Stage': ['Total Candidates', 'After Screening', 'After Interviews', 'Shortlisted', 'Joined'],
            'Count': [total_candidates, total_candidates - screening_rejected, total_candidates - screening_rejected - interview_rejected, shortlisted, joined]
        }
        funnel_df = pd.DataFrame(funnel_data)
        
        # Create left-aligned funnel chart using horizontal bar
        fig_funnel = px.bar(
            funnel_df,
            y='Stage',
            x='Count',
            orientation='h',
            color='Stage',
            color_discrete_sequence=['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6'],
            text='Count'
        )
        fig_funnel.update_layout(
            height=450,
            showlegend=False,
            xaxis_title="Number of Candidates",
            yaxis_title=None,
            xaxis=dict(
                showgrid=True, 
                gridcolor='#e5e7eb',
                range=[0, total_candidates * 1.15],  # Add 15% padding to show full bar with text
                fixedrange=True  # Disable zoom/pan
            ),
            yaxis=dict(
                categoryorder='array', 
                categoryarray=['Joined', 'Shortlisted', 'After Interviews', 'After Screening', 'Total Candidates'],
                fixedrange=True  # Disable zoom/pan
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=14, color='#1e293b'),
            margin=dict(l=20, r=50, t=10, b=50),  # Increased bottom margin to show x-axis
            autosize=True
        )
        fig_funnel.update_traces(
            textposition='outside',
            textfont=dict(size=18, color='#000000', family='Inter', weight='bold'),  # Changed to pure black and bold
            marker=dict(line=dict(width=0)),
            texttemplate='%{text}'
        )
        st.plotly_chart(fig_funnel, use_container_width=True)
    
    with col2:
        st.markdown("<h3 style='color: #1e293b; font-weight: 600;'>📌 Quick Stats</h3>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Quick stats cards
        pending_count = len(df[df['Dashboard_Category'] == 'Pending/Active'])
        conversion_rate = (joined / total_candidates * 100) if total_candidates > 0 else 0
        selection_rate = (shortlisted / total_candidates * 100) if total_candidates > 0 else 0
        
        st.markdown(f"""
        <div style='background: white; padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            <p style='color: #718096; margin: 0; font-size: 0.875rem;'>Pending Candidates</p>
            <h2 style='color: #2d3748; margin: 0.25rem 0 0 0; font-size: 2rem;'>{pending_count}</h2>
        </div>
        
        <div style='background: white; padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            <p style='color: #718096; margin: 0; font-size: 0.875rem;'>Conversion Rate</p>
            <h2 style='color: #48bb78; margin: 0.25rem 0 0 0; font-size: 2rem;'>{conversion_rate:.1f}%</h2>
        </div>
        
        <div style='background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            <p style='color: #718096; margin: 0; font-size: 0.875rem;'>Shortlist Rate</p>
            <h2 style='color: #4299e1; margin: 0.25rem 0 0 0; font-size: 2rem;'>{selection_rate:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)

# Tab 2: Candidate Metrics
with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #1e293b; font-weight: 600;'>📈 Performance Metrics</h3>", unsafe_allow_html=True)
    
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
        height=500
    )

# Tab 3: Detailed Records
with tab3:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #1e293b; font-weight: 600;'>📋 Complete Candidate Data</h3>", unsafe_allow_html=True)
    
    st.dataframe(
        df[['Candidate Name', 'HM Details', 'Skill', 'Status', 'Dashboard_Category', 'Recruiter Name']],
        use_container_width=True,
        height=500
    )