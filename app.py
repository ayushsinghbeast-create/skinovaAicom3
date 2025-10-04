import streamlit as st
import gspread
import pandas as pd
from PIL import Image
from io import StringIO, BytesIO
import random
from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt
import numpy as np
from gspread import Client, Spreadsheet, Worksheet

# --- 1. CONFIGURATION & HYPER-POLISHED UI SETUP ---

# Custom Colors
SOFT_BLUE = "#6EC1E4"
DARK_ACCENT = "#3C8CB0"
LIGHT_BG = "#F9FCFF"
TEXT_COLOR = "#333333"

# Page Configuration
st.set_page_config(
    page_title="SkinovaAI: Hyper-Personalized Skincare",
    page_icon="🧴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Extensive Custom CSS for Theme, Fonts, and Hyper-Polish
st.markdown(f"""
    <style>
    /* Global App Styling */
    .stApp {{
        background-color: {LIGHT_BG};
        color: {TEXT_COLOR};
        font-family: 'Inter', sans-serif;
    }}
    
    /* Sidebar Styling */
    .css-1d391kg, .css-1lcbmhc {{ /* Background and Text */
        background-color: {SOFT_BLUE};
        color: {LIGHT_BG};
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.15);
    }}
    .css-1oe2kgi a {{ /* Sidebar Links/Text */
        color: {LIGHT_BG} !important;
        font-weight: 500;
        border-radius: 6px;
        padding: 8px 10px;
        transition: all 0.2s ease;
    }}
    .css-1oe2kgi a:hover {{
        background-color: {DARK_ACCENT};
        transform: translateX(5px);
    }}
    .css-16weoif a {{ /* Active Sidebar Link */
        background-color: {DARK_ACCENT};
        border-left: 5px solid white;
        padding-left: 5px !important;
        font-weight: bold;
    }}
    
    /* Main Content Headers */
    h1 {{
        color: {DARK_ACCENT};
        font-size: 3em;
        border-bottom: 2px solid {SOFT_BLUE}20;
        padding-bottom: 10px;
    }}
    h2, h3 {{
        color: {TEXT_COLOR};
        margin-top: 1.5rem;
    }}
    
    /* Custom Card Design (Hyper-Card) */
    .skinova-card {{
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        margin-bottom: 25px;
        border-left: 6px solid {SOFT_BLUE};
        transition: all 0.3s ease;
    }}
    .skinova-card:hover {{
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }}

    /* Score Card Specific Styling */
    .score-display {{
        font-size: 70px;
        font-weight: 900;
        color: {SOFT_BLUE};
        text-shadow: 2px 2px 5px {DARK_ACCENT}50;
        line-height: 1;
    }}

    /* Buttons Styling */
    div.stButton > button:first-child {{
        background: linear-gradient(145deg, {SOFT_BLUE}, {DARK_ACCENT});
        color: {WHITE};
        border: none;
        border-radius: 10px;
        padding: 12px 25px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    div.stButton > button:first-child:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
    }}
    
    /* Progress Bar Color */
    .stProgress > div > div > div > div {{
        background-color: {DARK_ACCENT};
    }}
    </style>
    """, unsafe_allow_html=True)


# --- 2. GOOGLE SHEETS HYPER-INTEGRATION ---

# NOTE: Using Streamlit Secrets for robust deployment simulation.
# If running locally, you must create a dummy 'credentials.json' or define st.secrets.
try:
    gc: Client = gspread.service_account_from_dict(st.secrets.get("gcp_service_account", {}))
except Exception:
    # Local fallback or dummy connector logic
    class DummySheet:
        def get_all_records(self): return []
        def append_row(self, row): pass
        def row_values(self, row): return ['Name', 'Email', 'Age', 'Location', 'Concerns', 'Skin Score', 'Routine', 'Last Login']
        def update(self, range_name, values): pass
    class DummyWorksheet:
        def worksheet(self, title): return DummySheet()
    class DummyClient:
        def open_by_url(self, url): return DummyWorksheet()
        def worksheet(self, title): return DummySheet()
    gc = DummyClient()
    st.info("Using Dummy Google Sheet Connector. Data will not persist outside this session.")


SHEET_URL = "https://docs.google.com/spreadsheets/d/1FduUP69UAMYGTXoDGKHu9_Mhgyv3bWR1HJSle7t-iSs/edit?gid=0#gid=0"

try:
    sh: Spreadsheet = gc.open_by_url(SHEET_URL)
    worksheet: Worksheet = sh.worksheet("Users")
except Exception as e:
    st.error(f"Sheet Access Error: {e}")
    # Fallback to dummy sheet list for structure
    worksheet = DummySheet()
    
# Helper function to get the current date's string key
def get_today_key():
    return date.today().strftime("%Y-%m-%d")

# --- 3. SESSION STATE HYPER-INITIALIZATION ---

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_page = 'Login/Signup'
    st.session_state.user_email = None
    st.session_state.onboarding_complete = False
    st.session_state.user_data_profile = {}
    
    # Hyper-Routine Tracking (Detailed per step and date)
    st.session_state.daily_progress = {} # {'2025-10-01': [True, False, True, False, ...]}
    st.session_state.routine_streak = 0
    st.session_state.last_login_date = date.today()
    
    # Dummy Hyper-Score History (30 days)
    start_score = random.randint(60, 90)
    st.session_state.skin_score_history = [start_score + random.randint(-2, 3) for _ in range(30)]
    st.session_state.skin_score = st.session_state.skin_score_history[-1]


# --- 4. DATA UTILITY FUNCTIONS (Enhanced) ---

@st.cache_data(ttl=60)
def load_data():
    """Load the user data from Google Sheet into a DataFrame."""
    try:
        df = pd.DataFrame(worksheet.get_all_records())
        # Ensure all core columns exist, even if empty
        required_cols = ['Name', 'Email', 'Age', 'Location', 'Concerns', 'Skin Score', 'Routine', 'Last Login', 'Routine_Progress', 'Streak']
        for col in required_cols:
            if col not in df.columns:
                df[col] = ''
        return df
    except Exception as e:
        st.error(f"Error loading user data: {e}")
        return pd.DataFrame(columns=required_cols)

def get_user_row(email):
    """Retrieves the full DataFrame row for the logged-in user."""
    df = load_data()
    if email in df['Email'].values:
        return df[df['Email'] == email].iloc[0].to_dict()
    return {}

def save_user_data(email, update_dict):
    """
    Finds the user's row and updates specific columns.
    Handles data serialization for complex objects.
    """
    try:
        df = load_data()
        if df.empty or email not in df['Email'].values:
            st.error("Cannot save data: User not found or sheet error.")
            return False

        row_index = df[df['Email'] == email].index[0]
        row_num = row_index + 2 # +2 for 1-indexing and header row

        # Prepare update dictionary with potential serialization
        header = worksheet.row_values(1)
        update_list = worksheet.row_values(row_num)

        for col_name, value in update_dict.items():
            if col_name in header:
                col_index = header.index(col_name)
                # Serialize complex data types (lists, dicts)
                if isinstance(value, (list, dict)):
                    update_list[col_index] = str(value) # Using str() for simple dicts/lists
                else:
                    update_list[col_index] = str(value)
        
        # Ensure the list size matches the header size for safe update
        if len(update_list) < len(header):
             update_list.extend([''] * (len(header) - len(update_list)))

        worksheet.update(f'A{row_num}:Z{row_num}', [update_list])
        
        load_data.clear() # Invalidate cache
        return True

    except Exception as e:
        st.error(f"An error occurred during hyper-data save: {e}")
        return False

def parse_routine_progress(progress_str):
    """Parses the routine progress string back into a dictionary or list."""
    if not progress_str or progress_str == 'None':
        return {}
    try:
        return eval(progress_str) # Safely evaluate the string representation of dict/list
    except:
        return {}
        
def parse_score_history(history_str):
    """Parses the score history string back into a list of integers."""
    if not history_str:
        return [random.randint(60, 90) for _ in range(30)] # Default to dummy 30 days
    try:
        return [int(x.strip()) for x in history_str.strip('[]').split(',') if x.strip()]
    except:
        return [random.randint(60, 90) for _ in range(30)]

# --- 5. PAGE NAVIGATION & AUTH ---

def navigate_to(page):
    st.session_state.current_page = page

def logout():
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.session_state.user_data_profile = {}
    st.session_state.current_page = 'Login/Signup'
    st.experimental_rerun()

def initialize_user_session(email, user_data):
    """Initializes session state with hyper-user data upon login/signup."""
    st.session_state.logged_in = True
    st.session_state.user_email = email
    st.session_state.user_data_profile = user_data
    
    # Check if 'Age' column is filled to determine onboarding status
    st.session_state.onboarding_complete = bool(user_data.get('Age')) 
    
    # Load complex data structures
    st.session_state.daily_progress = parse_routine_progress(user_data.get('Routine_Progress', '{}'))
    st.session_state.routine_streak = int(user_data.get('Streak', 0))
    st.session_state.skin_score = int(user_data.get('Skin Score', random.randint(60, 90)))
    st.session_state.skin_score_history = parse_score_history(user_data.get('Score_History', ''))
    
    # Daily Login Streak Check and Score Update
    if 'Last Login' in user_data:
        last_login_dt = datetime.strptime(user_data['Last Login'], "%Y-%m-%d %H:%M:%S").date()
        today = date.today()
        
        # Streak maintenance/increase logic
        if last_login_dt == today:
            pass # Already logged in today
        elif last_login_dt == today - timedelta(days=1):
            st.session_state.routine_streak += 1
            st.toast(f"🔥 Streak maintained! Now at {st.session_state.routine_streak} days!", icon='🏆')
        else:
            if st.session_state.routine_streak > 0:
                st.toast(f"😔 Streak lost ({st.session_state.routine_streak} days). Start fresh today!", icon='💔')
            st.session_state.routine_streak = 1 # Start new streak

    save_user_data(email, {
        'Last Login': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'Streak': st.session_state.routine_streak
    })


# --- 6. CORE FEATURE FUNCTIONS (PAGES) ---

## 1. Login & Signup (Detailed UI/UX)
def login_signup_page():
    st.title("Welcome to SkinovaAI 🧴")
    st.subheader("Your Hyper-Personalized Skincare Journey Starts Here")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'<div class="skinova-card"><h3>Create Your Account (Signup)</h3></div>', unsafe_allow_html=True)
        with st.form("signup_form"):
            new_name = st.text_input("Full Name *", key="s_name")
            new_email = st.text_input("Email Address *", key="s_email")
            st.markdown("_Your email will be your unique identifier._")
            
            signup_submitted = st.form_submit_button("🚀 Create Account & Start Onboarding")

            if signup_submitted:
                df = load_data()
                if new_email in df['Email'].values:
                    st.error("🚫 Duplicate email entry. An account with this email already exists. Please log in.")
                elif not new_name or not new_email or '@' not in new_email:
                    st.warning("Please enter a valid Name and Email.")
                else:
                    # Initial data structure for new user
                    initial_score = random.randint(60, 85)
                    new_user_data = [
                        new_name, new_email, '', '', '', 
                        initial_score, 'Basic Routine: Cleanser, Moisturizer, SPF', 
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                        '{}', 1, f'[{initial_score}]' # Routine_Progress, Streak, Score_History
                    ]
                    worksheet.append_row(new_user_data)
                    st.success("🎉 Account created successfully! Redirecting to hyper-onboarding...")
                    
                    initialize_user_session(new_email, get_user_row(new_email))
                    navigate_to('Onboarding')
                    st.experimental_rerun()

    with col2:
        st.markdown(f'<div class="skinova-card"><h3>Existing User (Login)</h3></div>', unsafe_allow_html=True)
        with st.form("login_form"):
            login_email = st.text_input("Email Address *", key="l_email")
            
            login_submitted = st.form_submit_button("➡️ Login to Dashboard")
            
            if login_submitted:
                df = load_data()
                if login_email in df['Email'].values:
                    user_data = get_user_row(login_email)
                    initialize_user_session(login_email, user_data)

                    st.success("Welcome back! Redirecting...")
                    if st.session_state.onboarding_complete:
                        navigate_to('Dashboard')
                    else:
                        navigate_to('Onboarding')
                    st.experimental_rerun()
                else:
                    st.error("❌ Email not found. Please check your email or sign up.")

### ---
## 2. Onboarding (Multi-Step Hyper-Setup)
def onboarding_page():
    st.title("Hyper-Onboarding: 2-Minute Skin Setup 🧬")
    st.markdown("---")
    
    st.subheader("We need comprehensive data for the ultimate personalized routine.")
    
    tab1, tab2, tab3 = st.tabs(["Personal Info", "Concerns & History", "Lifestyle & Goals"])

    with st.form("onboarding_form", clear_on_submit=False):
        
        with tab1:
            st.markdown("### Step 1: Baseline Data")
            user_age = st.slider("1. Age", min_value=12, max_value=80, value=25)
            user_gender = st.selectbox("2. Biological Gender", ['Female', 'Male', 'Non-Binary', 'Prefer not to say'])
            user_location = st.selectbox("3. Current Climate/Location Type", 
                                          ['Tropical/Humid', 'Arid/Dry Desert', 'Temperate/Seasonal', 'Cold/Northern', 'Urban/Polluted'])
            user_skin_type = st.radio("4. Self-Assessed Skin Type", ['Very Dry', 'Dry/Normal', 'Combination (Oily T-Zone)', 'Oily'])
        
        with tab2:
            st.markdown("### Step 2: Skin History")
            concerns = st.multiselect("5. Primary Skin Concerns (Select 2-4)",
                                        ['Acne & Breakouts', 'Dryness & Dehydration', 'Redness & Sensitivity', 
                                         'Dark Spots/Pigmentation', 'Fine Lines & Wrinkles', 'Loss of Firmness', 'Oil Control'],
                                         default=['Acne & Breakouts'], max_selections=4)
            allergy = st.text_input("6. Known Product Allergies (e.g., Lanolin, fragrance)", "None")
            sensitivity_level = st.select_slider("7. Skin Sensitivity Level", options=['Low', 'Mild', 'Moderate', 'High'], value='Mild')
            history_products = st.checkbox("8. Used Retinoids/AHAs before?")
        
        with tab3:
            st.markdown("### Step 3: Goals & Habits")
            goal = st.selectbox("9. Primary Skincare Goal", ['Acne Clearing', 'Anti-Aging & Firming', 'Hydration & Barrier Repair', 'Brightening & Even Tone'])
            budget = st.select_slider("10. Expected Monthly Budget (USD)", options=['$20 - $50', '$50 - $100', '$100+'])
            
            st.markdown("---")
            submitted = st.form_submit_button("✅ Finalize Personalized Profile")

    if submitted:
        if not concerns or not goal:
            st.error("Please ensure you've selected your Primary Concerns and Goal.")
        else:
            # HYPER-SCORE INITIAL CALCULATION LOGIC
            base_score = 80 
            # Penalties based on input
            if 'Acne & Breakouts' in concerns or user_skin_type in ['Combination (Oily T-Zone)', 'Oily']: base_score -= 5
            if 'Redness & Sensitivity' in concerns or sensitivity_level in ['Moderate', 'High']: base_score -= 7
            if user_age >= 40 and 'Fine Lines & Wrinkles' in concerns: base_score -= 6
            # Bonus
            if history_products: base_score += 2 # Experienced user
            
            initial_score = max(55, min(90, base_score + random.randint(-4, 4)))
            
            # Dynamic Routine Suggestion (Saved as string)
            routine_steps = {
                'Morning': ['Cleanser (Gentle)', 'Vitamin C Serum', 'Hydrating SPF 50+'],
                'Evening': ['Oil Cleanser', 'Water-Based Cleanser', 'Targeted Treatment (e.g., Retinol/AHA)', 'Moisturizer (Repair)']
            }
            default_routine_str = str(routine_steps)

            update_dict = {
                'Age': user_age,
                'Location': user_location,
                'Skin_Type': user_skin_type,
                'Concerns': ", ".join(concerns),
                'Allergies': allergy,
                'Sensitivity': sensitivity_level,
                'Goal': goal,
                'Budget': budget,
                'Skin Score': initial_score,
                'Routine': default_routine_str, # Detailed Routine saved as string
                'Last Login': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            if save_user_data(st.session_state.user_email, update_dict):
                st.session_state.onboarding_complete = True
                st.session_state.skin_score = initial_score
                
                # Update history with new score
                st.session_state.skin_score_history.append(initial_score)
                st.session_state.skin_score_history = st.session_state.skin_score_history[-30:] # Keep last 30 days
                
                save_user_data(st.session_state.user_email, {
                    'Score_History': str(st.session_state.skin_score_history)
                })

                st.success("✅ Hyper-Setup complete! Redirecting to Dashboard...")
                navigate_to('Dashboard')
                st.experimental_rerun()
            else:
                st.error("Failed to save data. Please check connection.")

### ---
## 3. Dashboard (Metric-Rich Hyper-View)
def dashboard_page():
    st.title("Dashboard: Hyper-Progress Overview 📊")
    st.markdown("---")
    
    user_data = get_user_row(st.session_state.user_email)
    today_key = get_today_key()
    
    # Calculate Routine Progress %
    routine_steps = parse_routine_progress(user_data.get('Routine'))
    total_steps = sum(len(steps) for steps in routine_steps.values())
    
    # Calculate completed steps from today's progress log
    completed_steps = len([s for s in st.session_state.daily_progress.get(today_key, []) if s])
    
    routine_completion_percent = int((completed_steps / total_steps) * 100) if total_steps > 0 else 0


    st.subheader(f"Welcome back, **{user_data.get('Name', 'User')}**!")
    
    # 3-Column KPI Display
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="skinova-card" style="border-left: 6px solid #FFC300;">
            <p style='font-size: 16px; margin-bottom: 5px; font-weight: 600;'>Current Skin Score 🌟</p>
            <p class="score-display">{st.session_state.skin_score}</p>
            <p style='font-size: 12px; font-style: italic;'>Target: 95. Change: {st.session_state.skin_score_history[-1] - st.session_state.skin_score_history[-2] if len(st.session_state.skin_score_history) > 1 else 0} pts (24h)</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="skinova-card" style="border-left: 6px solid #4CAF50;">
            <p style='font-size: 16px; margin-bottom: 5px; font-weight: 600;'>Routine Compliance (Daily) 🎯</p>
            <p class="score-display" style='color: #4CAF50;'>{routine_completion_percent}%</p>
            <p style='font-size: 12px; font-style: italic;'>Completed {completed_steps}/{total_steps} steps today.</p>
        </div>
        """, unsafe_allow_html=True)
        st.progress(routine_completion_percent)

    with col3:
        st.markdown(f"""
        <div class="skinova-card" style="border-left: 6px solid #FF4B4B;">
            <p style='font-size: 16px; margin-bottom: 5px; font-weight: 600;'>Current Streak 🔥</p>
            <p class="score-display" style='color: #FF4B4B;'>{st.session_state.routine_streak}</p>
            <p style='font-size: 12px; font-style: italic;'>Keep going! Consistent care yields results.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("## 30-Day Skin Health Trend 📈")
    
    # Matplotlib Graph (30-Day Hyper-Trend)
    fig, ax = plt.subplots(figsize=(12, 5))
    
    scores = st.session_state.skin_score_history
    days = list(range(1, len(scores) + 1))
    
    ax.plot(days, scores, marker='o', linestyle='-', color=SOFT_BLUE, linewidth=3, markersize=6, alpha=0.7)
    
    # Add target line
    ax.axhline(90, color='grey', linestyle='--', alpha=0.5, label='Target Score (90)')
    
    ax.set_title('30-Day Skin Score Trend', fontsize=18, fontweight='bold', color=TEXT_COLOR)
    ax.set_xlabel('Day', fontsize=14)
    ax.set_ylabel('Skin Score', fontsize=14)
    ax.set_ylim(min(scores) - 5, max(scores) + 5)
    ax.grid(axis='y', linestyle=':', alpha=0.6)
    
    st.pyplot(fig)
    
    st.markdown("## Hyper-Insight: Your Profile Summary")
    with st.expander("Detailed Onboarding Data"):
        st.json({k: v for k, v in user_data.items() if k not in ['Routine_Progress', 'Score_History', 'Email']})


### ---
## 4. Skin Analyzer (Multi-Parameter AI Simulation)
def skin_analyzer_page():
    st.title("Skin Analyzer: AI-Powered Deep Scan 🔬")
    st.markdown("---")
    
    st.info("💡 **Hyper-Warning**: This simulation is for educational purposes. Always consult a dermatologist for real diagnosis.")
    
    uploaded_file = st.file_uploader("Upload a high-resolution, close-up image of your focus area.", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        
        st.markdown("---")
        
        col_img, col_proc = st.columns([1, 2])
        
        with col_img:
            st.image(image, caption='Image Submitted', use_column_width=True)
            
        with col_proc:
            st.markdown("### Processing Image with SkinovaNet 2.0 🤖")
            with st.spinner('Running multi-spectral analysis on 7 facial layers...'):
                import time
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.03)
                    progress_bar.progress(i + 1)
            progress_bar.empty()
            st.success("✅ Analysis Complete! Generating Report.")

        st.markdown("## 🔬 Comprehensive AI Scan Results")
        
        # Hyper-Detailed Dummy AI Logic
        dummy_results = {
            "Acne Index (P. Acnes Activity)": random.choice(["Low", "Mild", "Moderate", "High"]),
            "Pigmentation Index (Melanin Density)": random.choice(["Low", "Mild", "Moderate", "High"]),
            "Wrinkle Depth (Simulated)": random.choice(["Low", "Minimal", "Moderate", "Significant"]),
            "Pore Size & Clog Status": random.choice(["Tight & Clear", "Medium & Visible", "Enlarged & Clogged"]),
            "Hydration Level (Simulated Trans-Epidermal Water Loss)": random.choice(["Optimal (Level 5)", "Good (Level 4)", "Fair (Level 3)", "Poor (Level 2)"]),
            "Redness/Inflammation Index": random.choice(["Minimal", "Localized", "Diffuse"]),
        }
        
        # Determine the core issue for routine adjustment
        core_issue = max(dummy_results, key=lambda k: ["Low", "Minimal", "Good", "Optimal", "Fair", "Diffuse", "Moderate", "High", "Significant"].index(dummy_results[k]))
        
        routine_adjustment = ""
        if "Acne" in core_issue and dummy_results[core_issue] in ["Moderate", "High"]:
            routine_adjustment = "**Focus on BHA/Salicylic Acid and spot treatments.** Avoid heavy oils."
            suggested_routine = "Add 2% Salicylic Acid serum (PM) and switch to a Gel Cleanser."
        elif "Pigmentation" in core_issue and dummy_results[core_issue] in ["Moderate", "High"]:
            routine_adjustment = "**Intensify sun protection and use Tyrosinase Inhibitors.** Use SPF 50+ re-applied."
            suggested_routine = "Add 15% Vitamin C (AM) and use a high-strength Retinoid (PM)."
        elif "Wrinkle" in core_issue and dummy_results[core_issue] in ["Moderate", "Significant"]:
            routine_adjustment = "**Integrate high-grade Peptides and strong retinoids.** Focus on deep hydration."
            suggested_routine = "Introduce a Peptide Serum (AM) and a Prescription-Strength Retinoid (PM, 3x/week)."
        else:
            routine_adjustment = "Maintain current routine. Focus on hydration and prevention."
            suggested_routine = "Your skin is balanced! Continue with your core routine."

        # Display results in a table-like structure
        st.subheader("Key Biometric Indicators:")
        res_cols = st.columns(3)
        for i, (key, value) in enumerate(dummy_results.items()):
            color = "#4CAF50" if value.startswith(("Low", "Minimal", "Optimal", "Tight")) else ("#FFC300" if value.startswith(("Mild", "Medium", "Fair", "Localized")) else "#FF4B4B")
            with res_cols[i % 3]:
                 st.markdown(f"""
                <div class="skinova-card" style="padding: 15px; border-left: 5px solid {color};">
                    <p style='font-size: 14px; margin-bottom: 0; color: #777;'>{key}</p>
                    <p style='font-size: 18px; font-weight: bold; color: {color}; margin-top: 5px;'>{value}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class="skinova-card" style="margin-top: 20px; background-color: {SOFT_BLUE}10;">
                <h4 style='margin-top:0; color:{DARK_ACCENT}'>AI Hyper-Prescription Summary:</h4>
                <p style='font-size: 18px; font-weight: 500;'>**Core Issue Identified:** {core_issue}</p>
                <p style='font-size: 16px;'>**Actionable Adjustment:** {routine_adjustment}</p>
                <p style='font-size: 16px;'>**Suggested Routine Change:** *{suggested_routine}*</p>
            </div>
            """, unsafe_allow_html=True)
            
        # Store results in a separate "Analyzer_Logs" sheet (Hyper-Extension)
        try:
            log_sheet: Worksheet = sh.worksheet("Analyzer_Logs")
            new_log = [
                st.session_state.user_email, 
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                dummy_results['Acne Index (P. Acnes Activity)'],
                dummy_results['Pigmentation Index (Melanin Density)'],
                dummy_results['Wrinkle Depth (Simulated)'],
                suggested_routine
            ]
            log_sheet.append_row(new_log)
        except Exception:
            pass # Silent fail for dummy sheet
            
        # Button to automatically update the routine
        if st.button("Apply Suggested Routine Change", key='apply_routine'):
            # Fetch current routine steps and modify
            current_routine = parse_routine_progress(st.session_state.user_data_profile.get('Routine', '{}'))
            # Simple modification logic for demonstration
            if 'Salicylic Acid' in suggested_routine:
                if 'Evening' in current_routine:
                    current_routine['Evening'][2] = 'BHA/Salicylic Acid Treatment'
                else:
                    current_routine['Evening'] = ['Oil Cleanser', 'Water-Based Cleanser', 'BHA/Salicylic Acid Treatment', 'Moisturizer (Repair)']
            
            save_user_data(st.session_state.user_email, {'Routine': str(current_routine)})
            st.session_state.user_data_profile['Routine'] = str(current_routine) # Update session
            st.success("Routine successfully updated! Check 'My Routine' page.")
            navigate_to('My Routine')
            st.experimental_rerun()


### ---
## 5. My Routine (Dynamic & Streak-Driven Tracking)
def my_routine_page():
    st.title("My Daily Ritual Tracker ✅")
    st.markdown("---")

    user_data = get_user_row(st.session_state.user_email)
    
    # Dynamic Routine Steps
    routine_steps_dict = parse_routine_progress(user_data.get('Routine', '{}'))
    if not routine_steps_dict:
        st.warning("Your personalized routine is not set. Please complete Onboarding or run the Skin Analyzer.")
        return

    # Check for daily reset (if first login of the day or first visit to this page today)
    today_key = get_today_key()
    if today_key not in st.session_state.daily_progress:
        st.session_state.daily_progress[today_key] = [False] * sum(len(steps) for steps in routine_steps_dict.values())
        
    
    # Save the progress for the current day
    def update_progress():
        # Step 1: Calculate Routine Compliance Score for today
        total_steps = len(st.session_state.daily_progress.get(today_key, []))
        completed_steps = st.session_state.daily_progress[today_key].count(True)
        compliance_score = completed_steps / total_steps if total_steps > 0 else 0
        
        # Step 2: Calculate Score Boost/Drop (Hyper-Logic)
        score_change = 0
        if compliance_score == 1.0:
            score_change = 3
            st.balloons()
            st.success("✨ 100% Routine Compliance! +3 Score Boost!")
        elif compliance_score >= 0.75:
            score_change = 1
            st.info("👍 Excellent Compliance! +1 Score Boost.")
        elif compliance_score < 0.5 and completed_steps > 0:
            score_change = 0
        elif completed_steps == 0:
            score_change = -2
            st.warning("⚠️ No steps completed today. -2 Score Penalty.")

        # Step 3: Update Skin Score and History
        new_score = st.session_state.skin_score + score_change
        st.session_state.skin_score = max(50, min(99, new_score)) 
        
        # Update today's score in the history (which is the last element)
        if st.session_state.skin_score_history:
            st.session_state.skin_score_history[-1] = st.session_state.skin_score
        else:
            st.session_state.skin_score_history = [st.session_state.skin_score]

        # Step 4: Save all complex data back to the sheet
        save_user_data(st.session_state.user_email, {
            'Routine_Progress': str(st.session_state.daily_progress), # Save detailed progress history
            'Skin Score': st.session_state.skin_score,
            'Score_History': str(st.session_state.skin_score_history)
        })
        st.success("Routine progress and Skin Score updated successfully!")


    st.markdown(f"""
    <div class="skinova-card" style="border-left: 5px solid #FFD700;">
        <h4 style='margin-top:0; color:{DARK_ACCENT}'>Today's Focus: {user_data.get('Goal', 'Optimal Health')}</h4>
        <p>Current Streak: **{st.session_state.routine_streak} days** 🔥</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Use a persistent index counter to map check boxes to the daily_progress list
    step_index = 0
    
    col_m, col_e = st.columns(2)

    with col_m:
        st.subheader("☀️ Morning Routine (Protection Focus)")
        st.markdown("_Ensuring environmental defense and hydration._")
        for i, step in enumerate(routine_steps_dict.get('Morning', [])):
            st.session_state.daily_progress[today_key][step_index] = st.checkbox(f"**Step {i+1}**: {step}", 
                                                                                value=st.session_state.daily_progress[today_key][step_index],
                                                                                key=f"m_step_{step_index}", on_change=update_progress)
            step_index += 1

    with col_e:
        st.subheader("🌙 Evening Routine (Treatment Focus)")
        st.markdown("_Targeting concerns and facilitating overnight repair._")
        for i, step in enumerate(routine_steps_dict.get('Evening', [])):
            st.session_state.daily_progress[today_key][step_index] = st.checkbox(f"**Step {i+1}**: {step}", 
                                                                                value=st.session_state.daily_progress[today_key][step_index],
                                                                                key=f"e_step_{step_index}", on_change=update_progress)
            step_index += 1

    st.markdown("---")
    st.info("Check a box to instantly save and update your progress and Skin Score.")


### ---
## 6. Product Marketplace (Detailed Filtering and Cards)
def product_marketplace_page():
    st.title("Hyper-Marketplace: Curated Skincare Solutions 🛍️")
    st.markdown("---")
    
    # Hyper-Extension: Expanded product list (15+ items)
    products = [
        {"Name": "Barrier Repair Cleanser", "Price": "$25", "Concern": "Dryness & Dehydration", "Link": "https://amzn.to/d1", "Type": "Cleanser", "Key_Ingredients": "Ceramides, Glycerin"},
        {"Name": "BHA Pimple Serum", "Price": "$35", "Concern": "Acne & Breakouts", "Link": "https://nyka.com/d2", "Type": "Treatment", "Key_Ingredients": "Salicylic Acid, Niacinamide"},
        {"Name": "Pro-Retinol 0.5% Cream", "Price": "$50", "Concern": "Fine Lines & Wrinkles", "Link": "https://amzn.to/d3", "Type": "Treatment", "Key_Ingredients": "Retinol, Peptides"},
        {"Name": "Calm-Cica Gel", "Price": "$30", "Concern": "Redness & Sensitivity", "Link": "https://nyka.com/d4", "Type": "Moisturizer", "Key_Ingredients": "Centella Asiatica, Allantoin"},
        {"Name": "Ascorbic Acid 15% Serum", "Price": "$45", "Concern": "Dark Spots/Pigmentation", "Link": "https://amzn.to/d5", "Type": "Serum", "Key_Ingredients": "Vitamin C, Ferulic Acid"},
        {"Name": "Multi-Weight HA Booster", "Price": "$28", "Concern": "Dryness & Dehydration", "Link": "https://nyka.com/d6", "Type": "Serum", "Key_Ingredients": "Hyaluronic Acid, B5"},
        {"Name": "A-Zinc Oil Control Serum", "Price": "$30", "Concern": "Acne & Breakouts", "Link": "https://amzn.to/d7", "Type": "Serum", "Key_Ingredients": "Niacinamide, Zinc PCA"},
        {"Name": "Mineral Defense SPF 50", "Price": "$35", "Concern": "All", "Link": "https://nyka.com/d8", "Type": "Sunscreen", "Key_Ingredients": "Zinc Oxide, Titanium Dioxide"},
        {"Name": "Hydro-Repair Eye Cream", "Price": "$40", "Concern": "Fine Lines & Wrinkles", "Link": "https://amzn.to/d9", "Type": "Eye Care", "Key_Ingredients": "Peptides, Caffeine"},
        {"Name": "Deep Hydrating Toner", "Price": "$20", "Concern": "Dryness & Dehydration", "Link": "https://amzn.to/d10", "Type": "Toner", "Key_Ingredients": "Rose Water, Snail Mucin"},
    ]
    
    concern_options = ["All", 'Acne & Breakouts', 'Dryness & Dehydration', 'Fine Lines & Wrinkles', 'Redness & Sensitivity', 'Dark Spots/Pigmentation']
    type_options = ["All", "Cleanser", "Toner", "Serum", "Moisturizer", "Treatment", "Sunscreen", "Eye Care"]

    # Filtering UI
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        selected_concern = st.selectbox("Filter by Primary Concern", concern_options)
    with filter_col2:
        selected_type = st.selectbox("Filter by Product Type", type_options)
    
    filtered_products = products
    if selected_concern != "All":
        filtered_products = [p for p in filtered_products if selected_concern == p["Concern"]]
    if selected_type != "All":
        filtered_products = [p for p in filtered_products if selected_type == p["Type"]]
    
    st.subheader(f"Showing {len(filtered_products)} Curated Products")
    
    # Display products in a 3-column grid
    num_cols = 3
    
    for i in range(0, len(filtered_products), num_cols):
        cols = st.columns(num_cols)
        for j in range(num_cols):
            if i + j < len(filtered_products):
                product = filtered_products[i + j]
                with cols[j]:
                    st.markdown(f"""
                    <div class="skinova-card" style="min-height: 300px; border-left: 6px solid {DARK_ACCENT};">
                        <h4 style='color:{SOFT_BLUE}; margin-top:0;'>{product['Name']}</h4>
                        <p style='color: #4CAF50; font-weight: bold; font-size: 22px;'>{product['Price']}</p>
                        <p><strong>Type:</strong> {product['Type']}</p>
                        <p><strong>Target:</strong> {product['Concern']}</p>
                        <p style='font-size: 14px;'><strong>Key Ingredients:</strong> {product['Key_Ingredients']}</p>
                        <a href="{product['Link']}" target="_blank">
                            <button style="background-color: #FFC300; color: {TEXT_COLOR}; padding: 8px 15px; border: none; border-radius: 4px; cursor: pointer; margin-top: 10px;">
                                View & Buy (Affiliate)
                            </button>
                        </a>
                    </div>
                    """, unsafe_allow_html=True)

### ---
## 7. Personalized Kit (Complex Logic)
def personalized_kit_page():
    st.title("The Ultimate Personalized Skincare Kit 🎁")
    st.markdown("---")

    user_data = get_user_row(st.session_state.user_email)
    concerns = [c.strip() for c in user_data.get('Concerns', '').split(',') if c.strip()]
    sensitivity = user_data.get('Sensitivity', 'Mild')
    skin_type = user_data.get('Skin_Type', 'Combination')
    score = st.session_state.skin_score
    
    if not concerns:
        st.warning("Please complete onboarding to generate your hyper-kit.")
        return

    st.subheader(f"Analyzing {skin_type} skin with concerns: **{', '.join(concerns)}**")
    
    # HYPER-KIT GENERATION LOGIC
    kit = {}

    # 1. Cleanser (Based on Skin Type/Sensitivity)
    if 'Oily' in skin_type or 'Acne & Breakouts' in concerns:
        kit['Cleanser'] = ('Gel-to-Foam Clarifying Cleanser', 'Salicylic Acid, Willow Bark')
    elif 'Dry' in skin_type or sensitivity == 'High':
        kit['Cleanser'] = ('Creamy Hydrating Cleansing Balm', 'Ceramides, Oat Extract')
    else:
        kit['Cleanser'] = ('Gentle pH-Balanced Cleanser', 'Glycerin, Niacinamide')

    # 2. AM Serum (Based on Primary Goal/Concern)
    if 'Brightening' in user_data.get('Goal', '') or 'Pigmentation' in concerns:
        kit['AM_Serum'] = ('15% L-Ascorbic Acid Serum', 'Vitamin C, Ferulic Acid')
    elif 'Anti-Aging' in user_data.get('Goal', ''):
        kit['AM_Serum'] = ('Peptide & Growth Factor Serum', 'Copper Peptides, Hyaluronic Acid')
    else:
        kit['AM_Serum'] = ('Niacinamide 10% Barrier Serum', 'Niacinamide, Zinc PCA')

    # 3. Moisturizer (Based on Skin Type)
    if 'Oily' in skin_type or 'Combination' in skin_type:
        kit['Moisturizer'] = ('Oil-Free Water Gel Moisturizer', 'Hyaluronic Acid, Amino Acids')
    else:
        kit['Moisturizer'] = ('Ceramide-Rich Repair Cream', 'Ceramides, Squalane')

    # 4. Sun Protection (Mandatory & Enhanced)
    kit['Sunscreen'] = ('Broad Spectrum Mineral SPF 50+', 'Zinc Oxide, Tinted Formula')

    # 5. PM Treatment (The 'Heavy Lifter' - Based on Score/Concern)
    if 'Acne & Breakouts' in concerns and score < 75:
        kit['PM_Treatment'] = ('Benzoyl Peroxide Spot Treatment', 'Benzoyl Peroxide 5%')
    elif 'Wrinkles' in concerns or 'Anti-Aging' in user_data.get('Goal', ''):
        kit['PM_Treatment'] = ('Time-Release Retinaldehyde Cream', 'Retinaldehyde, Bakuchiol')
    else:
        kit['PM_Treatment'] = ('AHA/BHA Gentle Exfoliating Toner', 'Lactic Acid, Glycolic Acid')
        
    st.markdown("Based on your **concerns**, **skin type**, and **score**, here is your 5-step optimized kit:")
    
    kit_cols = st.columns(3)
    
    items = list(kit.items())
    for i, (key, (product_name, ingredients)) in enumerate(items):
        with kit_cols[i % 3]:
            st.markdown(f"""
            <div class="skinova-card" style="min-height: 200px; background-color: {LIGHT_BG};">
                <h5 style='color:{SOFT_BLUE}; margin-bottom: 5px;'>{key.replace('_', ' ').upper()}</h5>
                <p style='font-weight: bold; font-size: 18px;'>{product_name}</p>
                <p style='font-size: 14px;'>**Key Ingredients:** {ingredients}</p>
                <p style='font-size: 12px; font-style: italic;'>*Hyper-Rationale: {key.split('_')[0]} product selection.*</p>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("---")
    
    # Buy Now Section
    st.subheader("Ready to Check Out?")
    affiliate_link = "https://affiliate.link/skinovakit-hyper-bundle-v2" # Dummy Link
    st.markdown(f"""
        <a href="{affiliate_link}" target="_blank">
            <button style="background-color: #FF4B4B; color: white; padding: 15px 30px; border: none; border-radius: 10px; cursor: pointer; font-size: 20px; font-weight: bold; margin-top: 10px;">
                🛒 Secure Your 5-Piece Hyper-Kit Now!
            </button>
        </a>
    """, unsafe_allow_html=True)


### ---
## 8. Skincare Academy (Comprehensive Learning Module)
def skincare_academy_page():
    st.title("Skincare Academy: Hyper-Learning Module 🎓")
    st.markdown("---")
    
    tab_vid, tab_art, tab_quiz = st.tabs(["📺 Deep-Dive Videos", "📚 Advanced Articles", "🧠 Certification Quiz"])
    
    with tab_vid:
        st.header("Video Tutorials: Beyond the Basics")
        
        col_v1, col_v2 = st.columns(2)
        
        with col_v1:
            st.subheader("1. Decoding TEWL (Water Loss)")
            st.components.v1.iframe("https://www.youtube.com/embed/g8l9_F-x_Yw", height=250)
            st.markdown("Understand Trans-Epidermal Water Loss and how to combat it with occlusives.")
            
        with col_v2:
            st.subheader("2. Barrier Function & Ceramides")
            st.components.v1.iframe("https://www.youtube.com/embed/q4X0Qo-D5Yk", height=250)
            st.markdown("The science of skin barrier repair and the essential role of Ceramides.")

        st.subheader("3. Sunscreen Filters: Chemical vs. Physical")
        st.components.v1.iframe("https://www.youtube.com/embed/4y8w0fD8lIw", height=250)
        st.markdown("Which filter is right for your skin type and sun exposure level?")

    with tab_art:
        st.header("Advanced Skincare Articles")
        st.markdown("---")
        st.subheader("Article 1: Micro-Dosing Retinoids for Sensitive Skin")
        st.markdown("""
        Micro-dosing involves using small amounts of retinoids multiple times a week instead of a high concentration daily. 
        **Why it works:** It allows the skin to acclimatize to the ingredient with minimal irritation, maximizing long-term benefits 
        such as collagen production and cell turnover without the common "retinoid uglies" (flaking, redness).
        """)
        st.markdown("---")
        st.subheader("Article 2: Glycation and Anti-Aging (A.G.E.s)")
        st.markdown("""
        Advanced Glycation End products (A.G.E.s) are formed when sugar molecules bond with proteins (like collagen and elastin) 
        in the skin, causing them to stiffen and lose elasticity. This process is a major contributor to intrinsic aging. 
        **How to fight it:** While difficult to reverse, topical antioxidants and lifestyle adjustments (like diet control) can mitigate the damage.
        """)
        st.markdown("---")
        st.subheader("Article 3: Niacinamide: The Holy Grail for Combination Skin")
        st.markdown("""
        Niacinamide (Vitamin B3) is a versatile powerhouse. It helps reduce pore size, strengthens the skin barrier, 
        improves redness, and regulates oil production. Its ability to manage both oil control (T-zone) and barrier function (dry areas) 
        makes it the perfect ingredient for complex combination skin types.
        """)
        st.markdown("---")
        st.subheader("Article 4: Hydroquinone Alternatives for Stubborn Melasma")
        st.markdown("""
        While Hydroquinone remains the gold standard, alternatives like **Kojic Acid, Azelaic Acid, and Cysteamine** are highly effective. 
        These work by inhibiting the Tyrosinase enzyme, which is crucial for melanin production, offering powerful pigment control without the associated risks of long-term Hydroquinone use.
        """)

    with tab_quiz:
        st.header("Skinova Master Quiz (5 Questions)")
        st.markdown("Answer correctly to receive a **+5 Skin Score bonus**!")
        
        quiz_questions = [
            ("The 'gold standard' ingredient for stimulating collagen and increasing cell turnover is:", ["Vitamin C", "Hyaluronic Acid", "Retinoids", "Glycerin"], "Retinoids"),
            ("What is the primary function of a **humectant**?", ["Exfoliation", "Moisture Attraction", "Oil Sealing", "UV Absorption"], "Moisture Attraction"),
            ("What does TEWL stand for?", ["T-Zone Water Loss", "Total Exfoliation Width", "Trans-Epidermal Water Loss", "Toxin Elimination Waste Loop"], "Trans-Epidermal Water Loss"),
            ("Which ingredient is best for soothing redness and sensitive skin?", ["Glycolic Acid", "Benzoyl Peroxide", "Centella Asiatica (Cica)", "Denatured Alcohol"], "Centella Asiatica (Cica)"),
            ("Which type of sunscreen filter works by absorbing UV radiation and converting it into heat?", ["Physical/Mineral", "Chemical/Organic"], "Chemical/Organic")
        ]
        
        # State to store answers and score
        if 'quiz_score' not in st.session_state:
            st.session_state.quiz_score = None
            st.session_state.quiz_answers = {}

        with st.form("master_quiz_form"):
            user_answers = {}
            for i, (q, options, _) in enumerate(quiz_questions):
                user_answers[f'q{i+1}'] = st.radio(f"{i+1}. {q}", options, key=f"quiz_q{i+1}")
            
            quiz_submitted = st.form_submit_button("Submit Master Quiz")
            
            if quiz_submitted:
                final_score = 0
                st.session_state.quiz_answers = user_answers
                
                for i, (_, _, correct_answer) in enumerate(quiz_questions):
                    q_key = f'q{i+1}'
                    if st.session_state.quiz_answers.get(q_key) == correct_answer:
                        final_score += 1

                st.session_state.quiz_score = final_score
                
                # Feedback and Score Update
                st.subheader(f"Quiz Results: {final_score}/{len(quiz_questions)}")
                if final_score == len(quiz_questions):
                    if final_score is not None and final_score == len(quiz_questions):
                        st.balloons()
                        st.success("🏆 Perfect Score! You're a Skinova Certified Expert! +5 Skin Score awarded.")
                        
                        # Update Score Logic
                        st.session_state.skin_score = min(99, st.session_state.skin_score + 5)
                        st.session_state.skin_score_history[-1] = st.session_state.skin_score
                        save_user_data(st.session_state.user_email, {
                            'Skin Score': st.session_state.skin_score,
                            'Score_History': str(st.session_state.skin_score_history)
                        })
                    else:
                         st.info("Great job! Review the questions you missed for full certification.")
                else:
                    st.error("Needs Improvement. Try again after reviewing the academy.")
                
                # Show Feedback
                for i, (q, _, correct_answer) in enumerate(quiz_questions):
                    q_key = f'q{i+1}'
                    user_ans = st.session_state.quiz_answers.get(q_key)
                    is_correct = user_ans == correct_answer
                    feedback_icon = "✅" if is_correct else "❌"
                    st.markdown(f"**{feedback_icon} Q{i+1}:** {q} (Your Answer: {user_ans}. Correct: **{correct_answer}**)")


### ---
## 9. Community Forum (Basic CRUD Simulation)
def community_forum_page():
    st.title("Community Forum: Connect & Share 💬")
    st.markdown("---")
    
    st.subheader("Post a Question for Peer Review")
    
    try:
        forum_sheet: Worksheet = sh.worksheet("Forum_Posts")
        forum_sheet.get_all_records() # Check if it works
    except Exception:
        st.warning("Forum sheet not accessible. Posts will be saved temporarily in session only.")
        forum_sheet = None
        if 'temp_forum' not in st.session_state:
            st.session_state.temp_forum = []


    with st.form("post_question_form"):
        post_title = st.text_input("Title of your question (e.g., Retinol Purge?)", max_chars=100)
        post_content = st.text_area("Your full question/concern (Max 500 chars)", height=150, max_chars=500)
        post_submitted = st.form_submit_button("Submit Question to Forum")
        
        if post_submitted:
            if not post_title or not post_content:
                st.warning("Please fill in both the title and your question.")
            else:
                new_post = {
                    'User_Email': st.session_state.user_email,
                    'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'Post_Title': post_title,
                    'Post_Content': post_content
                }
                
                if forum_sheet:
                    forum_sheet.append_row(list(new_post.values()))
                    st.success("✅ Your question has been posted to the live sheet!")
                else:
                    st.session_state.temp_forum.append(new_post)
                    st.success("✅ Your question has been saved locally (Sheet not connected).")
                
                # Clear form inputs after successful submission
                st.session_state["post_title_key"] = ""
                st.session_state["post_content_key"] = ""
                st.experimental_rerun()
                
    st.markdown("---")
    
    st.subheader("🔥 Latest Community Questions")

    forum_data = pd.DataFrame()
    if forum_sheet:
        try:
            forum_data = pd.DataFrame(forum_sheet.get_all_records())
        except Exception:
            st.error("Error loading forum data from sheet.")
            
    if not forum_data.empty:
        # Combine sheet data with session data for the user
        if forum_sheet is None and st.session_state.temp_forum:
             forum_data = pd.concat([forum_data, pd.DataFrame(st.session_state.temp_forum)])

        recent_posts = forum_data.sort_values(by='Timestamp', ascending=False).head(8)
        
        for index, row in recent_posts.iterrows():
            with st.expander(f"**{row['Post_Title']}** - *Posted by {row['User_Email']} on {row['Timestamp'][:10]}*"):
                st.markdown(row['Post_Content'])
                st.markdown("---")
                st.markdown(f"_Dummy Replies: 3, Last Activity: Just Now_")
    else:
        st.info("No questions posted yet. Be the first to start the conversation!")


### ---
## 10. Consult an Expert (Enhanced Form)
def consult_expert_page():
    st.title("Consult a Skinova Expert 👩‍⚕️")
    st.markdown("---")
    
    st.subheader("Book Your Virtual 1-on-1 Session")
    st.markdown("Provide detailed information below for our experts to prepare a hyper-personalized plan before your call.")

    try:
        consult_sheet: Worksheet = sh.worksheet("Expert_Consults")
    except Exception:
        consult_sheet = None

    user_data = get_user_row(st.session_state.user_email)

    with st.form("consult_form"):
        st.markdown("### Your Details")
        con_name = st.text_input("Your Full Name", value=user_data.get('Name', ''), disabled=True)
        con_email = st.text_input("Your Email", value=user_data.get('Email', ''), disabled=True)
        
        st.markdown("### Consultation Focus")
        concern_type = st.selectbox("Type of Consultation", ['Routine Review & Optimization', 'Acne Management', 'Anti-Aging Strategies', 'Product Allergy Check'])
        con_concern = st.text_area("Describe your concern/question in detail", height=200)
        
        st.markdown("### Optional: Provide Visual Context")
        uploaded_image = st.file_uploader("Upload a high-res image of the area (Optional)", type=["jpg", "jpeg", "png"])
        
        consult_submitted = st.form_submit_button("Submit Consultation Request")

        if consult_submitted:
            if not con_concern:
                st.warning("Please describe your concern.")
            elif consult_sheet:
                # Log image upload status, as we can't save the image data to the sheet
                image_status = "Image attached" if uploaded_image else "No image attached"
                
                new_consult = [
                    con_name,
                    con_email,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    concern_type,
                    con_concern,
                    image_status
                ]
                consult_sheet.append_row(new_consult)
                
                st.success("✅ Your consultation request has been submitted!")
                st.markdown(f"""
                <div class="skinova-card" style="background-color: #4CAF5010; border-left: 5px solid #4CAF50;">
                    <p style='font-weight: bold;'>Confirmation:</p>
                    <p>Our expert team has received your request regarding **{concern_type}**.</p>
                    <p>They will contact you within **24 hours** to schedule a video call and share your preliminary analysis.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("Failed to save consultation request. Google Sheet not connected.")


# --- 7. MAIN APP ROUTER ---

# Sidebar Navigation (Always Visible)
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <h2 style="color: white; margin: 0;">SKINOVAAI</h2>
        <p style="color: #FFFFFF90; font-size: 14px;">HYPER-PERSONALIZED CARE</p>
    </div>
    <hr style="border-top: 1px solid #FFFFFF50;"/>
    """, unsafe_allow_html=True)

    if st.session_state.logged_in:
        st.markdown(f"**Current User:** {st.session_state.user_email}", unsafe_allow_html=True)
        st.markdown(f"**Score:** {st.session_state.skin_score} | **Streak:** {st.session_state.routine_streak} 🔥", unsafe_allow_html=True)
        st.markdown("---")
        
        pages = {
            'Dashboard': '📊 Dashboard',
            'My Routine': '✅ My Daily Ritual',
            'Skin Analyzer': '🔬 Hyper-Analyzer',
            'Personalized Kit': '🎁 Personalized Kit',
            'Product Marketplace': '🛍️ Marketplace',
            'Skincare Academy': '👩‍🎓 Skincare Academy',
            'Community Forum': '💬 Community Forum',
            'Consult an Expert': '👩‍⚕️ Consult an Expert'
        }
        
        if not st.session_state.onboarding_complete:
            st.warning("⚠️ Complete Onboarding!")
            selected_page = 'Onboarding'
        else:
            selected_page = st.radio(
                "Navigation Menu", 
                options=list(pages.keys()), 
                format_func=lambda x: pages[x],
                index=list(pages.keys()).index(st.session_state.current_page) if st.session_state.current_page in pages else 0
            )
        
        navigate_to(selected_page)
        
        st.markdown("---")
        if st.button("🚪 Logout", help="Log out of the application"):
            logout()
            
    else:
        st.info("Please Login or Signup to access the Hyper-Platform.")
        if st.button("Start My Journey"):
            navigate_to('Login/Signup')


# Main Content Display
if st.session_state.logged_in:
    if not st.session_state.onboarding_complete and st.session_state.current_page != 'Onboarding':
        onboarding_page() # Force redirect to onboarding
    elif st.session_state.current_page == 'Onboarding':
        onboarding_page()
    elif st.session_state.current_page == 'Dashboard':
        dashboard_page()
    elif st.session_state.current_page == 'My Routine':
        my_routine_page()
    elif st.session_state.current_page == 'Skin Analyzer':
        skin_analyzer_page()
    elif st.session_state.current_page == 'Personalized Kit':
        personalized_kit_page()
    elif st.session_state.current_page == 'Product Marketplace':
        product_marketplace_page()
    elif st.session_state.current_page == 'Skincare Academy':
        skincare_academy_page()
    elif st.session_state.current_page == 'Community Forum':
        community_forum_page()
    elif st.session_state.current_page == 'Consult an Expert':
        consult_expert_page()
else:
    login_signup_page()
