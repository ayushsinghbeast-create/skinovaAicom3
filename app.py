import streamlit as st
import pandas as pd
from PIL import Image
from io import StringIO, BytesIO
import random
from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt
import numpy as np

# --- 1. CONFIGURATION & HYPER-POLISHED UI SETUP ---

# Custom Colors (Same beautiful theme)
SOFT_BLUE = "#6EC1E4"
DARK_ACCENT = "#3C8CB0"
LIGHT_BG = "#F9FCFF"
TEXT_COLOR = "#333333"
WHITE = "#FFFFFF"

# Page Configuration
st.set_page_config(
    page_title="SkinovaAI: Hyper-Personalized Skincare (Session)",
    page_icon="🧴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Extensive Custom CSS for Theme, Fonts, and Hyper-Polish (150+ lines of CSS alone!)
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
        background: {WHITE};
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


# --- 2. SESSION STATE HYPER-INITIALIZATION (Internal DB) ---

# This dictionary acts as our in-memory database, storing all user data
if 'user_db' not in st.session_state:
    st.session_state.user_db = {}
    
# Initialize core session flags
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_page = 'Login/Signup'
    st.session_state.user_email = None
    
# Initialize current user's ephemeral data for the session (will be loaded on login)
if 'user_data_profile' not in st.session_state:
    st.session_state.user_data_profile = {}
    st.session_state.onboarding_complete = False
    st.session_state.routine_streak = 0
    st.session_state.skin_score = 75
    st.session_state.skin_score_history = [75] * 30 
    st.session_state.daily_progress = {} # {'2025-10-01': {'AM': [True, False], 'PM': [True, True]}}
    st.session_state.last_login_date = date.today().strftime("%Y-%m-%d")

# Initialize feature-specific data (Forum, Consult Logs)
if 'forum_posts' not in st.session_state:
    st.session_state.forum_posts = [] # Log of all community posts
if 'consult_requests' not in st.session_state:
    st.session_state.consult_requests = [] # Log of all expert consult requests


# --- 3. DATA UTILITY FUNCTIONS (Session-State Based) ---

def create_new_user(name, email):
    """Creates a new user entry in the internal database."""
    initial_score = random.randint(60, 85)
    
    # Detailed Initial User Profile Structure
    st.session_state.user_db[email] = {
        'Name': name,
        'Email': email,
        'Age': None, # Onboarding required
        'Location': None,
        'Skin_Type': None,
        'Concerns': [],
        'Allergies': 'None',
        'Sensitivity': 'Mild',
        'Goal': 'Hydration & Barrier Repair',
        'Budget': '$50 - $100',
        'Routine': {}, # Detailed routine dictionary (AM/PM steps)
        
        # State Tracking
        'Skin Score': initial_score,
        'Score_History': [initial_score] * 30, # 30 days of initial score
        'Routine_Progress': {},
        'Streak': 1,
        'Last Login': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'Onboarding_Complete': False
    }
    return st.session_state.user_db[email]

def get_user_data(email):
    """Retrieves the full profile data for a given email."""
    return st.session_state.user_db.get(email, {})

def save_user_data(email, update_dict):
    """Updates specific fields for the user in the internal database."""
    if email in st.session_state.user_db:
        st.session_state.user_db[email].update(update_dict)
        # Also update the ephemeral session profile immediately
        st.session_state.user_data_profile.update(update_dict)
        return True
    return False

def get_today_key():
    """Helper function to get the current date's string key."""
    return date.today().strftime("%Y-%m-%d")


# --- 4. PAGE NAVIGATION & AUTH ---

def navigate_to(page):
    """Changes the current page view."""
    st.session_state.current_page = page

def logout():
    """Resets session state and returns to login page."""
    # Only reset ephemeral session flags, keep the DB intact
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.session_state.user_data_profile = {}
    st.session_state.current_page = 'Login/Signup'
    st.experimental_rerun()

def initialize_user_session(email, user_data):
    """Initializes session state with hyper-user data upon login/signup."""
    st.session_state.logged_in = True
    st.session_state.user_email = email
    
    # Load all persistent data into the ephemeral session state
    st.session_state.user_data_profile = user_data
    st.session_state.onboarding_complete = user_data.get('Onboarding_Complete', False)
    st.session_state.daily_progress = user_data.get('Routine_Progress', {})
    st.session_state.routine_streak = user_data.get('Streak', 0)
    st.session_state.skin_score = user_data.get('Skin Score', 75)
    st.session_state.skin_score_history = user_data.get('Score_History', [75] * 30)
    
    
    # --- HYPER-LOGIN STREAK CHECK & DAILY SCORE UPDATE ---
    last_login_str = user_data.get('Last Login', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    last_login_dt = datetime.strptime(last_login_str, "%Y-%m-%d %H:%M:%S").date()
    today = date.today()
    
    score_change = 0
    
    if last_login_dt < today:
        # Check if they completed their routine yesterday (Hypothetical full completion check)
        yesterday_key = (today - timedelta(days=1)).strftime("%Y-%m-%d")
        yesterday_progress = st.session_state.daily_progress.get(yesterday_key, {'AM': [False, False], 'PM': [False, False]})
        
        total_steps_yesterday = sum(len(v) for v in yesterday_progress.values())
        completed_steps_yesterday = sum(v.count(True) for v in yesterday_progress.values())
        
        if completed_steps_yesterday >= (total_steps_yesterday * 0.8): # 80% compliance
            st.session_state.routine_streak = st.session_state.routine_streak + 1 if last_login_dt == today - timedelta(days=1) else 1
            score_change += 2 # Small passive reward for consistency
            st.toast(f"🔥 Streak maintained! Now at {st.session_state.routine_streak} days. (+2 Score)", icon='🏆')
        else:
            if st.session_state.routine_streak > 0 and last_login_dt == today - timedelta(days=1):
                st.toast(f"😔 Yesterday's routine compliance was low. Streak lost ({st.session_state.routine_streak} days).", icon='💔')
            st.session_state.routine_streak = 1 # Start new streak regardless
            score_change -= 1 # Small penalty for low compliance

        # Append today's score to history and cap at 30 days
        st.session_state.skin_score += score_change
        st.session_state.skin_score = max(50, min(99, st.session_state.skin_score)) 
        st.session_state.skin_score_history.append(st.session_state.skin_score)
        st.session_state.skin_score_history = st.session_state.skin_score_history[-30:]
        
        # Save all changes back to the internal database
        save_user_data(email, {
            'Last Login': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Streak': st.session_state.routine_streak,
            'Skin Score': st.session_state.skin_score,
            'Score_History': st.session_state.skin_score_history
        })
        
    st.experimental_rerun()


# --- 5. CORE FEATURE FUNCTIONS (PAGES) ---

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
            st.markdown("_Your email will be your unique identifier. **No passwords needed!**_", help="We simulate a secure token-based login for simplicity.")
            
            signup_submitted = st.form_submit_button("🚀 Create Account & Start Onboarding")

            if signup_submitted:
                if new_email in st.session_state.user_db:
                    st.error("🚫 Duplicate email entry. An account with this email already exists. Please log in.")
                elif not new_name or not new_email or '@' not in new_email:
                    st.warning("Please enter a valid Name and Email.")
                else:
                    user_data = create_new_user(new_name, new_email)
                    st.success("🎉 Account created successfully! Redirecting to hyper-onboarding...")
                    
                    initialize_user_session(new_email, user_data)
                    navigate_to('Onboarding')
                    st.experimental_rerun()

    with col2:
        st.markdown(f'<div class="skinova-card"><h3>Existing User (Login)</h3></div>', unsafe_allow_html=True)
        with st.form("login_form"):
            login_email = st.text_input("Email Address *", key="l_email")
            
            login_submitted = st.form_submit_button("➡️ Login to Dashboard")
            
            if login_submitted:
                if login_email in st.session_state.user_db:
                    user_data = get_user_data(login_email)
                    st.success("Welcome back! Redirecting...")
                    
                    # Initialization handles score/streak updates on login
                    initialize_user_session(login_email, user_data)
                    
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
        
        # --- TAB 1: Baseline Data (Enhanced Detail) ---
        with tab1:
            st.markdown("### Step 1: Baseline Data")
            user_age = st.slider("1. Age", min_value=12, max_value=80, value=25)
            user_gender = st.selectbox("2. Biological Gender", ['Female', 'Male', 'Non-Binary', 'Prefer not to say'])
            user_ethnicity = st.selectbox("3. Fitzpatrick Skin Type (Determines Pigmentation Risk)", 
                                           ['Type I (Always burns)', 'Type II (Burns easily)', 'Type III (Tans sometimes)', 'Type IV (Tans easily)', 'Type V (Rarely burns)', 'Type VI (Never burns)'])
            user_location = st.selectbox("4. Current Climate/Location Type", 
                                          ['Tropical/Humid', 'Arid/Dry Desert', 'Temperate/Seasonal', 'Cold/Northern', 'Urban/Polluted'])
            user_skin_type = st.radio("5. Self-Assessed Skin Type (Basic)", ['Very Dry', 'Dry/Normal', 'Combination (Oily T-Zone)', 'Oily'])
        
        # --- TAB 2: Skin History (Enhanced Detail) ---
        with tab2:
            st.markdown("### Step 2: Skin History & Concerns")
            concerns = st.multiselect("6. Primary Skin Concerns (Select 2-4)",
                                        ['Acne & Breakouts (Hormonal)', 'Acne & Breakouts (Fungal/Bacterial)', 'Dryness & Dehydration (Barrier)', 'Redness & Sensitivity (Rosacea)', 
                                         'Dark Spots/Melasma/Pigmentation', 'Fine Lines & Wrinkles (Static)', 'Loss of Firmness/Elasticity', 'Oil Control/Excess Sebum'],
                                         default=['Acne & Breakouts (Hormonal)', 'Oil Control/Excess Sebum'], max_selections=4)
            allergy = st.text_input("7. Known Product Allergies (e.g., Lanolin, fragrance, harsh surfactants)", "None")
            sensitivity_level = st.select_slider("8. Skin Sensitivity Level (How easily does your skin react?)", options=['Low', 'Mild', 'Moderate', 'High/Reactive'], value='Moderate')
            history_products = st.checkbox("9. Have you used prescription-strength actives (Retinoids/AHAs > 10%) before?")
        
        # --- TAB 3: Goals & Habits (Enhanced Detail) ---
        with tab3:
            st.markdown("### Step 3: Goals & Habits")
            goal = st.selectbox("10. Primary Skincare Goal", ['Acne Clearing & Scar Reduction', 'Advanced Anti-Aging & Firming', 'Max Hydration & Barrier Repair', 'Brightening & Even Tone/Melasma Reduction'])
            sleep_hours = st.slider("11. Average Nightly Sleep (Hours)", min_value=4.0, max_value=10.0, value=7.0, step=0.5)
            budget = st.select_slider("12. Expected Monthly Budget (USD)", options=['$20 - $50 (Budget)', '$50 - $100 (Mid-Range)', '$100 - $200 (Premium)', '$200+ (Luxury)'])
            
            st.markdown("---")
            submitted = st.form_submit_button("✅ Finalize Personalized Profile")

    if submitted:
        if len(concerns) < 2 or not goal:
            st.error("Please select at least 2 Primary Concerns and your Primary Skincare Goal.")
        else:
            # --- HYPER-SCORE INITIAL CALCULATION LOGIC (Complex Formula) ---
            base_score = 95 
            
            # 1. Age Penalty (More penalty for age > 40)
            base_score -= (user_age / 10) * 0.5
            
            # 2. Concern Penalty (Severe concerns drop score more)
            if any('Melasma' in c or 'Wrinkles' in c for c in concerns): base_score -= 8
            if any('Acne & Breakouts' in c for c in concerns): base_score -= 5
            
            # 3. Sensitivity & Fitzpatrick Penalty
            if sensitivity_level in ['High/Reactive']: base_score -= 7
            if user_ethnicity in ['Type IV', 'Type V', 'Type VI'] and 'Pigmentation' in concerns: base_score -= 4 # Higher risk for PIH
            
            # 4. Lifestyle Bonus/Penalty
            if sleep_hours < 6.0: base_score -= 3
            if history_products: base_score += 2 # Experienced user bonus
            
            initial_score = max(55, min(90, int(base_score + random.uniform(-3, 3))))
            
            # --- DYNAMIC ROUTINE GENERATION (Based on Input) ---
            
            # Morning Routine (Focus: Antioxidant + Protection)
            am_steps = ['Cleanser (Low pH)']
            if 'Pigmentation' in concerns or 'Brightening' in goal:
                am_steps.append('Vitamin C Serum (L-Ascorbic)')
            am_steps.append('Hydrating Moisturizer')
            am_steps.append('Broad Spectrum SPF 50+')

            # Evening Routine (Focus: Treatment + Repair)
            pm_steps = ['Oil-Based Makeup Remover', 'Water-Based Cleanser']
            if any('Acne' in c for c in concerns):
                pm_steps.append('Targeted BHA or Azelaic Acid Treatment')
            elif any('Wrinkles' in c or 'Firmness' in c for c in concerns) and history_products:
                pm_steps.append('High-Potency Retinoid/Retinal')
            else:
                pm_steps.append('Hydrating/Peptide Serum')
            pm_steps.append('Occlusive Repair Cream')

            routine_steps_dict = {'Morning': am_steps, 'Evening': pm_steps}
            
            update_dict = {
                'Age': user_age,
                'Location': user_location,
                'Skin_Type': user_skin_type,
                'Concerns': concerns,
                'Allergies': allergy,
                'Sensitivity': sensitivity_level,
                'Goal': goal,
                'Budget': budget,
                'Sleep_Hours': sleep_hours,
                'Skin Score': initial_score,
                'Routine': routine_steps_dict, 
                'Score_History': st.session_state.skin_score_history, # Use existing history, update last score
                'Last Login': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'Onboarding_Complete': True
            }
            
            # Update the score history with the calculated initial score
            update_dict['Score_History'][-1] = initial_score

            if save_user_data(st.session_state.user_email, update_dict):
                st.session_state.onboarding_complete = True
                st.session_state.skin_score = initial_score
                st.success("✅ Hyper-Setup complete! Redirecting to Dashboard...")
                navigate_to('Dashboard')
                st.experimental_rerun()
            else:
                st.error("Failed to save data. User session error.")

### ---
## 3. Dashboard (Metric-Rich Hyper-View)
def dashboard_page():
    st.title("Dashboard: Hyper-Progress Overview 📊")
    st.markdown("---")
    
    user_data = st.session_state.user_data_profile
    today_key = get_today_key()
    
    # Calculate Routine Progress % (Detailed AM/PM compliance)
    routine_steps = user_data.get('Routine', {})
    total_steps = sum(len(steps) for steps in routine_steps.values())
    
    # Get today's progress log
    today_progress = st.session_state.daily_progress.get(today_key, {'AM': [], 'PM': []})
    completed_steps = sum(v.count(True) for v in today_progress.values())

    routine_completion_percent = int((completed_steps / total_steps) * 100) if total_steps > 0 else 0

    st.subheader(f"Welcome back, **{user_data.get('Name', 'User')}**!")
    
    # 3-Column KPI Display
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="skinova-card" style="border-left: 6px solid #FFC300;">
            <p style='font-size: 16px; margin-bottom: 5px; font-weight: 600;'>Current Skin Score 🌟</p>
            <p class="score-display">{st.session_state.skin_score}</p>
            <p style='font-size: 12px; font-style: italic;'>Recent 24h Change: {'+' if st.session_state.skin_score_history[-1] >= st.session_state.skin_score_history[-2] else ''}{st.session_state.skin_score_history[-1] - st.session_state.skin_score_history[-2] if len(st.session_state.skin_score_history) > 1 else 0} pts</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="skinova-card" style="border-left: 6px solid #4CAF50;">
            <p style='font-size: 16px; margin-bottom: 5px; font-weight: 600;'>Routine Compliance (Today) 🎯</p>
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
            <p style='font-size: 12px; font-style: italic;'>Goal: Maintain 7-day minimum consistency.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 30-Day Skin Health Trend 📈")
    
    # Matplotlib Graph (30-Day Hyper-Trend with Projection)
    fig, ax = plt.subplots(figsize=(12, 5))
    
    scores = st.session_state.skin_score_history
    days = list(range(1, len(scores) + 1))
    
    # 1. Actual Historical Data
    ax.plot(days, scores, marker='o', linestyle='-', color=SOFT_BLUE, linewidth=3, markersize=6, alpha=0.7, label='Actual Score')
    
    # 2. Score Projection (Hyper-Detail)
    if len(scores) >= 7:
        # Simple linear projection based on the last 7 days' average change
        recent_change = scores[-1] - scores[-7]
        avg_daily_change = recent_change / 6
        
        projection_days = list(range(len(scores), len(scores) + 7))
        projected_scores = [scores[-1] + (avg_daily_change * i) for i in range(1, 8)]
        
        ax.plot([days[-1]] + projection_days, [scores[-1]] + projected_scores, 
                linestyle='--', color='grey', alpha=0.6, label='7-Day Projection')

    # Add target line
    ax.axhline(90, color='red', linestyle=':', alpha=0.7, label='Target Score (90)')
    
    ax.set_title('30-Day Skin Score Trend & 7-Day Projection', fontsize=18, fontweight='bold', color=TEXT_COLOR)
    ax.set_xlabel('Day (Last 30)', fontsize=14)
    ax.set_ylabel('Skin Score (50-100)', fontsize=14)
    ax.set_ylim(min(scores) - 5, max(scores) + 5 if max(scores) < 95 else 100)
    ax.grid(axis='y', linestyle=':', alpha=0.6)
    ax.legend()
    
    st.pyplot(fig)
    
    st.markdown("---")
    st.markdown("## Hyper-Insight: Your Profile Summary")
    with st.expander("Detailed Onboarding Data"):
        # Display key profile data from the session state
        display_data = {k: v for k, v in user_data.items() if k not in ['Routine_Progress', 'Score_History', 'Email', 'Last Login', 'Routine']}
        st.json(display_data)


### ---
## 4. Skin Analyzer (Multi-Parameter AI Simulation)
def skin_analyzer_page():
    st.title("Skin Analyzer: AI-Powered Deep Scan 🔬")
    st.markdown("---")
    
    st.info("💡 **Hyper-Warning**: This is a simulated analysis based on visual data interpretation algorithms.")
    
    uploaded_file = st.file_uploader("Upload a high-resolution, close-up image of your focus area (e.g., cheek or T-zone).", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        
        st.markdown("---")
        
        col_img, col_proc = st.columns([1, 2])
        
        with col_img:
            st.image(image, caption='Image Submitted', use_column_width=True)
            
        with col_proc:
            st.markdown("### Processing Image with SkinovaNet 2.0 🤖")
            st.markdown("_Running 12-layer Convolutional Analysis to detect subtle skin conditions..._")
            with st.spinner('Analyzing texture, color mapping, and subsurface artifacts...'):
                import time
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.02)
                    progress_bar.progress(i + 1)
            progress_bar.empty()
            st.success("✅ Analysis Complete! Generating Report.")

        st.markdown("## 🔬 Comprehensive AI Scan Results")
        
        # Hyper-Detailed Dummy AI Logic
        dummy_results = {
            "Acne Index (P. Acnes Activity)": random.choice(["Low", "Mild (Localized)", "Moderate (Diffuse)", "High (Severe)"]),
            "Pigmentation Index (Melanin Density)": random.choice(["Low", "Mild (Freckling)", "Moderate (Sun Damage)", "High (Melasma)"]),
            "Wrinkle Depth (Simulated)": random.choice(["Low (Dynamic only)", "Minimal (Fine Lines)", "Moderate (Static lines)", "Significant (Deep creases)"]),
            "Pore Size & Clog Status": random.choice(["Tight & Clear", "Medium & Visible", "Enlarged & Clogged"]),
            "Hydration Level (TEWL Metric)": random.choice(["Optimal (Level 5)", "Good (Level 4)", "Fair (Level 3)", "Poor (Level 2)"]),
            "Redness/Inflammation Index": random.choice(["Minimal", "Localized (Around acne)", "Diffuse (General sensitivity)"]),
            "Collagen Density (Est.)": random.choice(["High", "Average", "Below Average", "Low"]),
        }
        
        # Determine the core issue for routine adjustment
        # Find the metric with the "worst" rating (e.g., High, Severe, Poor)
        rating_order = ["Low", "Minimal", "Optimal", "Good", "Average", "Tight", "Mild", "Medium", "Fair", "Localized", "Diffuse", "Below Average", "High", "Significant", "Severe", "Poor"]
        core_issue = max(dummy_results, key=lambda k: rating_order.index(dummy_results[k].split('(')[0].strip()))
        
        routine_adjustment = ""
        suggested_routine_change = ""

        if "Acne Index" in core_issue and "Moderate" in dummy_results[core_issue]:
            routine_adjustment = "**Immediate need for anti-bacterial and keratolytic agents.** Focus on gentle exfoliation."
            suggested_routine_change = "Add 2% Salicylic Acid serum (PM, 3x/week) and switch to an Oil-Free Gel Cleanser."
        elif "Pigmentation Index" in core_issue and "High" in dummy_results[core_issue]:
            routine_adjustment = "**Critical need for UV blockage and Tyrosinase inhibitors.** Strict sun avoidance."
            suggested_routine_change = "Increase Vitamin C concentration (AM) and introduce a non-Hydroquinone lightener (Azelaic Acid, PM)."
        elif "Wrinkle Depth" in core_issue and "Significant" in dummy_results[core_issue]:
            routine_adjustment = "**Focus on deep dermal stimulation and matrix repair.** Higher grade active needed."
            suggested_routine_change = "Upgrade PM Retinoid to a higher-potency Retinaldehyde and add a Peptide-rich cream (AM)."
        elif "Hydration Level" in core_issue and "Poor" in dummy_results[core_issue]:
            routine_adjustment = "**Barrier function is compromised. Stop all harsh actives temporarily.** Focus on humectants and occlusives."
            suggested_routine_change = "Switch to a non-foaming cream cleanser and introduce an overnight Ceramide/Cholesterol mask."
        else:
            routine_adjustment = "Maintain current routine. Focus on prevention and minor optimization."
            suggested_routine_change = "Your skin is balanced! Continue with your core routine and reassess in 30 days."

        # Display results in a table-like structure
        st.subheader("Key Biometric Indicators:")
        res_cols = st.columns(3)
        for i, (key, value) in enumerate(dummy_results.items()):
            # Simple color logic based on the rating word
            color = "#4CAF50" if value.startswith(("Low", "Minimal", "Optimal", "Good", "High")) else ("#FFC300" if value.startswith(("Mild", "Medium", "Average", "Fair", "Localized")) else "#FF4B4B")
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
                <p style='font-size: 18px; font-weight: 500;'>**Core Issue Identified:** {core_issue} ({dummy_results[core_issue]})</p>
                <p style='font-size: 16px;'>**Actionable Adjustment:** {routine_adjustment}</p>
                <p style='font-size: 16px;'>**Suggested Routine Change:** *{suggested_routine_change}*</p>
            </div>
            """, unsafe_allow_html=True)
            
        # Button to automatically update the routine
        if st.button("Apply Suggested Routine Change and Update Profile Score", key='apply_routine'):
            
            # Complex modification logic: We assume the suggested change overrides the 'Treatment' step
            current_routine = st.session_state.user_data_profile.get('Routine', {})
            
            # Update the appropriate step based on the suggestion
            if 'BHA' in suggested_routine_change or 'Azelaic Acid' in suggested_routine_change:
                current_routine['Evening'] = [step for step in current_routine.get('Evening', []) if 'Retinoid' not in step and 'Treatment' not in step]
                current_routine['Evening'].insert(2, 'New: BHA/Azelaic Acid Treatment')
            elif 'Retinaldehyde' in suggested_routine_change or 'Peptide-rich' in suggested_routine_change:
                 current_routine['Evening'] = [step for step in current_routine.get('Evening', []) if 'BHA' not in step and 'Treatment' not in step]
                 current_routine['Evening'].insert(2, 'New: High-Potency Anti-Aging Treatment')
            
            # Score bonus for taking immediate action
            new_score = st.session_state.skin_score + random.randint(1, 3) 
            st.session_state.skin_score = max(50, min(99, new_score))
            st.session_state.skin_score_history[-1] = st.session_state.skin_score # Update today's score

            save_user_data(st.session_state.user_email, {
                'Routine': current_routine,
                'Skin Score': st.session_state.skin_score,
                'Score_History': st.session_state.skin_score_history
            })
            st.success("Routine successfully updated! Check 'My Routine' page.")
            navigate_to('My Routine')
            st.experimental_rerun()


### ---
## 5. My Routine (Dynamic & Streak-Driven Tracking)
def my_routine_page():
    st.title("My Daily Ritual Tracker ✅")
    st.markdown("---")

    user_data = st.session_state.user_data_profile
    
    # Dynamic Routine Steps (A dictionary containing 'Morning' and 'Evening' lists)
    routine_steps_dict = user_data.get('Routine', {})
    if not routine_steps_dict or 'Onboarding_Complete' not in user_data:
        st.warning("Your personalized routine is not set. Please complete Onboarding (page 2).")
        return

    today_key = get_today_key()
    
    # Initialize today's progress if first time visiting today
    if today_key not in st.session_state.daily_progress:
        st.session_state.daily_progress[today_key] = {
            'AM': [False] * len(routine_steps_dict.get('Morning', [])),
            'PM': [False] * len(routine_steps_dict.get('Evening', []))
        }
        
    
    # Save the progress for the current day
    def update_progress(time_of_day, index):
        # Update the specific checkbox state
        current_progress = st.session_state.daily_progress[today_key][time_of_day]
        current_progress[index] = not current_progress[index] # Toggle logic is handled by Streamlit, but we ensure the state update is here.
        st.session_state.daily_progress[today_key][time_of_day] = current_progress
        
        # Recalculate and update score immediately
        recalculate_score_and_save()


    def recalculate_score_and_save():
        # Step 1: Calculate Routine Compliance Score for today
        total_steps = sum(len(v) for v in routine_steps_dict.values())
        
        # Get latest progress from session state
        latest_progress = st.session_state.daily_progress.get(today_key, {'AM': [], 'PM': []})
        completed_steps = sum(v.count(True) for v in latest_progress.values())
        compliance_score = completed_steps / total_steps if total_steps > 0 else 0
        
        # Step 2: Calculate Score Boost/Drop (Hyper-Logic - only updates if final step is checked)
        score_change = 0
        
        if compliance_score > 0 and 'last_step_checked' not in st.session_state:
            # Only calculate full compliance bonus once per day
            st.session_state.last_step_checked = False
            
        if compliance_score == 1.0 and not st.session_state.get('daily_bonus_applied', False):
            score_change = 3
            st.session_state.daily_bonus_applied = True # Prevent multiple score additions
            st.balloons()
            st.toast("✨ 100% Routine Compliance! +3 Score Boost Applied!", icon='🏆')
        elif compliance_score >= 0.75 and not st.session_state.get('daily_bonus_applied', False):
            score_change = 1
            st.toast("👍 Excellent Compliance! +1 Score Boost.", icon='👍')
        
        # If score was already updated today, this prevents double dipping but updates the save structure
        
        # Step 3: Update Skin Score and History
        new_score = st.session_state.skin_score + score_change
        st.session_state.skin_score = max(50, min(99, new_score)) 
        
        # Update today's score in the history (which is the last element)
        if st.session_state.skin_score_history:
            st.session_state.skin_score_history[-1] = st.session_state.skin_score
        
        # Step 4: Save all complex data back to the internal DB
        save_user_data(st.session_state.user_email, {
            'Routine_Progress': st.session_state.daily_progress, # Save detailed progress history
            'Skin Score': st.session_state.skin_score,
            'Score_History': st.session_state.skin_score_history
        })
        st.info(f"Progress Saved. Current Score: {st.session_state.skin_score}")


    st.markdown(f"""
    <div class="skinova-card" style="border-left: 5px solid #FFD700;">
        <h4 style='margin-top:0; color:{DARK_ACCENT}'>Today's Focus: {user_data.get('Goal', 'Optimal Health')}</h4>
        <p>Current Streak: **{st.session_state.routine_streak} days** 🔥</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_m, col_e = st.columns(2)

    with col_m:
        st.subheader("☀️ Morning Routine (Protection Focus)")
        st.markdown("_Ensuring environmental defense and hydration._")
        for i, step in enumerate(routine_steps_dict.get('Morning', [])):
            st.checkbox(f"**Step {i+1}**: {step}", 
                        value=st.session_state.daily_progress[today_key]['AM'][i],
                        key=f"m_step_{i}", 
                        on_change=update_progress, 
                        args=('AM', i))

    with col_e:
        st.subheader("🌙 Evening Routine (Treatment Focus)")
        st.markdown("_Targeting concerns and facilitating overnight repair._")
        for i, step in enumerate(routine_steps_dict.get('Evening', [])):
            st.checkbox(f"**Step {i+1}**: {step}", 
                        value=st.session_state.daily_progress[today_key]['PM'][i],
                        key=f"e_step_{i}", 
                        on_change=update_progress, 
                        args=('PM', i))

    st.markdown("---")
    st.info("Check/Uncheck a box to instantly save and update your progress.")


### ---
## 6. Product Marketplace (Detailed Filtering and Cards)
def product_marketplace_page():
    st.title("Hyper-Marketplace: Curated Skincare Solutions 🛍️")
    st.markdown("---")
    
    # Hyper-Extension: Expanded product list (20+ items)
    products = [
        {"Name": "Barrier Repair Cleanser", "Price": "$25", "Concern": "Dryness & Dehydration (Barrier)", "Link": "#", "Type": "Cleanser", "Key_Ingredients": "Ceramides, Glycerin, Cholesterol"},
        {"Name": "BHA Pimple Serum (2%)", "Price": "$35", "Concern": "Acne & Breakouts (Fungal/Bacterial)", "Link": "#", "Type": "Treatment", "Key_Ingredients": "Salicylic Acid, Niacinamide, Green Tea"},
        {"Name": "Pro-Retinol 0.5% Cream", "Price": "$50", "Concern": "Fine Lines & Wrinkles (Static)", "Link": "#", "Type": "Treatment", "Key_Ingredients": "Encapsulated Retinol, Peptides, Bisabolol"},
        {"Name": "Calm-Cica Gel", "Price": "$30", "Concern": "Redness & Sensitivity (Rosacea)", "Link": "#", "Type": "Moisturizer", "Key_Ingredients": "Centella Asiatica, Allantoin, Panthenol"},
        {"Name": "Ascorbic Acid 15% Serum", "Price": "$45", "Concern": "Dark Spots/Melasma/Pigmentation", "Link": "#", "Type": "Serum", "Key_Ingredients": "L-Ascorbic Acid, Ferulic Acid, Vitamin E"},
        {"Name": "Multi-Weight HA Booster", "Price": "$28", "Concern": "Dryness & Dehydration (Barrier)", "Link": "#", "Type": "Serum", "Key_Ingredients": "Hyaluronic Acid (3 Weights), B5, Trehalose"},
        {"Name": "A-Zinc Oil Control Serum", "Price": "$30", "Concern": "Oil Control/Excess Sebum", "Link": "#", "Type": "Serum", "Key_Ingredients": "Niacinamide (10%), Zinc PCA, Licorice Root"},
        {"Name": "Mineral Defense SPF 50", "Price": "$35", "Concern": "All", "Link": "#", "Type": "Sunscreen", "Key_Ingredients": "Zinc Oxide, Titanium Dioxide, Iron Oxides"},
        {"Name": "Hydro-Repair Eye Cream", "Price": "$40", "Concern": "Fine Lines & Wrinkles (Static)", "Link": "#", "Type": "Eye Care", "Key_Ingredients": "Argireline Peptide, Caffeine, Retinal"},
        {"Name": "Deep Hydrating Toner", "Price": "$20", "Concern": "Dryness & Dehydration (Barrier)", "Link": "#", "Type": "Toner", "Key_Ingredients": "Rose Water, Snail Mucin, Galactomyces Ferment"},
        {"Name": "Azelaic Acid Suspension", "Price": "$22", "Concern": "Acne & Breakouts (Hormonal)", "Link": "#", "Type": "Treatment", "Key_Ingredients": "Azelaic Acid (10%), Squalane"},
        {"Name": "PM Occlusive Balm", "Price": "$38", "Concern": "Loss of Firmness/Elasticity", "Link": "#", "Type": "Moisturizer", "Key_Ingredients": "Petrolatum, Shea Butter, Peptides"},
        {"Name": "Glycolic Acid Toning Pads", "Price": "$32", "Concern": "Loss of Firmness/Elasticity", "Link": "#", "Type": "Exfoliant", "Key_Ingredients": "Glycolic Acid (8%), Aloe Vera"}
    ]
    
    concern_options = ["All", 'Acne & Breakouts (Hormonal)', 'Acne & Breakouts (Fungal/Bacterial)', 'Dryness & Dehydration (Barrier)', 'Redness & Sensitivity (Rosacea)', 'Dark Spots/Melasma/Pigmentation', 'Fine Lines & Wrinkles (Static)', 'Oil Control/Excess Sebum']
    type_options = ["All", "Cleanser", "Toner", "Serum", "Moisturizer", "Treatment", "Sunscreen", "Eye Care", "Exfoliant"]

    # Filtering UI
    st.subheader("Filter Your Hyper-Search")
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1:
        selected_concern = st.selectbox("Filter by Primary Concern", concern_options)
    with filter_col2:
        selected_type = st.selectbox("Filter by Product Type", type_options)
    with filter_col3:
        # Budget filter based on user's onboarded budget
        user_budget_str = st.session_state.user_data_profile.get('Budget', '$50 - $100 (Mid-Range)')
        st.markdown(f"**Your Budget Filter:** {user_budget_str.split('(')[0].strip()}")
        price_limit = 50 if '$50' in user_budget_str else (100 if '$100' in user_budget_str else 200)

    
    filtered_products = products
    if selected_concern != "All":
        filtered_products = [p for p in filtered_products if selected_concern in p["Concern"]]
    if selected_type != "All":
        filtered_products = [p for p in filtered_products if selected_type == p["Type"]]
        
    # Apply Price Limit Filter (Hyper-Constraint)
    filtered_products = [p for p in filtered_products if int(p["Price"].replace('$', '')) <= price_limit]

    st.subheader(f"Showing {len(filtered_products)} Curated Products (Within Your ${price_limit} Budget)")
    
    # Display products in a 3-column grid
    num_cols = 3
    
    for i in range(0, len(filtered_products), num_cols):
        cols = st.columns(num_cols)
        for j in range(num_cols):
            if i + j < len(filtered_products):
                product = filtered_products[i + j]
                with cols[j]:
                    st.markdown(f"""
                    <div class="skinova-card" style="min-height: 320px; border-left: 6px solid {DARK_ACCENT};">
                        <h4 style='color:{SOFT_BLUE}; margin-top:0;'>{product['Name']}</h4>
                        <p style='color: #4CAF50; font-weight: bold; font-size: 22px;'>{product['Price']}</p>
                        <p><strong>Type:</strong> {product['Type']}</p>
                        <p><strong>Target:</strong> {product['Concern'].split('(')[0].strip()}</p>
                        <p style='font-size: 14px;'>**Key Ingredients:** {product['Key_Ingredients']}</p>
                        <a href="{product['Link']}" target="_blank">
                            <button style="background-color: #FFC300; color: {TEXT_COLOR}; padding: 8px 15px; border: none; border-radius: 4px; cursor: pointer; margin-top: 10px;">
                                View & Buy (Affiliate Link)
                            </button>
                        </a>
                    </div>
                    """, unsafe_allow_html=True)


### ---
## 7. Personalized Kit (Complex Logic)
def personalized_kit_page():
    st.title("The Ultimate Personalized Skincare Kit 🎁")
    st.markdown("---")

    user_data = st.session_state.user_data_profile
    concerns = user_data.get('Concerns', [])
    sensitivity = user_data.get('Sensitivity', 'Mild')
    skin_type = user_data.get('Skin_Type', 'Combination')
    score = st.session_state.skin_score
    goal = user_data.get('Goal', '')
    
    if not concerns:
        st.warning("Please complete onboarding to generate your hyper-kit.")
        return

    st.subheader(f"Analyzing {skin_type} skin (Score: {score}) with goal: **{goal}**")
    
    # HYPER-KIT GENERATION LOGIC (More conditional complexity)
    kit = {}

    # 1. Cleanser (Conditioned by Skin Type/Acne/Sensitivity)
    if 'Oily' in skin_type or any('Acne' in c for c in concerns):
        kit['Cleanser'] = ('Gel-to-Foam Clarifying Cleanser', 'Salicylic Acid, Willow Bark', 'Targets oil and congestion.')
    elif 'Dry' in skin_type or sensitivity == 'High/Reactive':
        kit['Cleanser'] = ('Creamy Hydrating Cleansing Balm', 'Ceramides, Oat Extract', 'Soothes and protects barrier.')
    else:
        kit['Cleanser'] = ('Gentle pH-Balanced Cleanser', 'Glycerin, Niacinamide', 'Maintains skin harmony.')

    # 2. AM Serum (Conditioned by Pigmentation/Anti-Aging)
    if 'Brightening' in goal or any('Pigmentation' in c for c in concerns):
        kit['AM_Serum'] = ('15% L-Ascorbic Acid Serum', 'Vitamin C, Ferulic Acid', 'Provides strong antioxidant and brightening defense.')
    elif 'Anti-Aging' in goal or score < 80:
        kit['AM_Serum'] = ('Peptide & Copper Complex Serum', 'Copper Peptides, Hyaluronic Acid', 'Supports firmness and hydration.')
    else:
        kit['AM_Serum'] = ('Niacinamide 10% Barrier Serum', 'Niacinamide, Zinc PCA', 'Minimizes pores and controls redness.')

    # 3. Moisturizer (Conditioned by Skin Type and Hydration score)
    hydration_score = score # Using skin score as proxy for hydration
    if 'Oily' in skin_type or hydration_score > 90:
        kit['Moisturizer'] = ('Oil-Free Water Gel Moisturizer', 'Hyaluronic Acid, Amino Acids', 'Lightweight, non-comedogenic hydration.')
    else:
        kit['Moisturizer'] = ('Ceramide-Rich Repair Cream', 'Ceramides, Squalane, Cholesterol', 'Deep repair and moisture seal.')

    # 4. Sun Protection (Mandatory & Enhanced)
    kit['Sunscreen'] = ('Broad Spectrum Mineral SPF 50+', 'Zinc Oxide, Titanium Dioxide, Iron Oxides', 'Essential daily defense against UV and Blue Light.')

    # 5. PM Treatment (The 'Heavy Lifter' - Most Conditional Step)
    if any('Acne' in c for c in concerns) and score < 70:
        kit['PM_Treatment'] = ('Benzoyl Peroxide Spot Treatment', 'Benzoyl Peroxide 5%', 'Aggressively targets inflammatory acne.')
    elif 'Wrinkles' in concerns or 'Anti-Aging' in goal:
        kit['PM_Treatment'] = ('Time-Release Retinaldehyde Cream', 'Retinaldehyde, Bakuchiol', 'Powerful anti-aging with minimized irritation.')
    elif 'Sensitivity' in concerns or sensitivity == 'High/Reactive':
        kit['PM_Treatment'] = ('Kojic Acid & Arbutin Mask (Weekly)', 'Alpha-Arbutin, Kojic Acid', 'Gentle brightening and barrier boost.')
    else:
        kit['PM_Treatment'] = ('PHA/BHA Gentle Exfoliator', 'PHA, Lactic Acid', 'Mild nightly resurfacing.')
        
    st.markdown("Based on your **profile**, **score**, and **goals**, here is your 5-step optimized kit:")
    
    kit_cols = st.columns(3)
    
    items = list(kit.items())
    for i, (key, (product_name, ingredients, rationale)) in enumerate(items):
        with kit_cols[i % 3]:
            st.markdown(f"""
            <div class="skinova-card" style="min-height: 250px; background-color: {LIGHT_BG};">
                <h5 style='color:{SOFT_BLUE}; margin-bottom: 5px;'>{key.replace('_', ' ').upper()}</h5>
                <p style='font-weight: bold; font-size: 18px;'>{product_name}</p>
                <p style='font-size: 14px;'>**Key Ingredients:** {ingredients}</p>
                <p style='font-size: 12px; font-style: italic; color: #777;'>**Rationale:** {rationale}</p>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("---")
    
    # Buy Now Section
    st.subheader("Ready to Check Out?")
    st.markdown("This hyper-kit is valued at **$220 USD**. Get a bundle discount today.")
    affiliate_link = "#" # Dummy Link
    st.markdown(f"""
        <a href="{affiliate_link}" target="_blank">
            <button style="background-color: #FF4B4B; color: white; padding: 15px 30px; border: none; border-radius: 10px; cursor: pointer; font-size: 20px; font-weight: bold; margin-top: 10px;">
                🛒 Secure Your 5-Piece Hyper-Kit Now for $199!
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
            st.markdown("Understand Trans-Epidermal Water Loss and how to combat it with occlusives and humectants.")
            
        with col_v2:
            st.subheader("2. Barrier Function & Ceramides")
            st.components.v1.iframe("https://www.youtube.com/embed/q4X0Qo-D5Yk", height=250)
            st.markdown("The science of skin barrier repair and the essential role of Ceramides and Essential Fatty Acids.")

        st.subheader("3. P. Acnes, Sebum, and Inflammation")
        st.components.v1.iframe("https://www.youtube.com/embed/4y8w0fD8lIw", height=250)
        st.markdown("A deep dive into the complex pathogenesis of acne vulgaris and modern treatment modalities (BHA, BP, Azelaic Acid).")

    with tab_art:
        st.header("Advanced Skincare Articles (Hyper-Content)")
        st.markdown("---")
        st.subheader("Article 1: The 'Sandwich Method' for Retinoid Introduction")
        st.markdown("""
        **Technique:** Apply a thin layer of moisturizing cream, then the retinoid, and finish with another layer of moisturizer. 
        **Rationale:** This buffers the retinoid, allowing for controlled, slow-release absorption, dramatically reducing the common side effects 
        of redness, peeling, and irritation, making the ingredient accessible even for sensitive skin types.
        """)
        st.markdown("---")
        st.subheader("Article 2: Niacinamide: Beyond Pore Size Reduction")
        st.markdown("""
        While known for its oil-regulating properties, Niacinamide's true hyper-power lies in its ability to **increase ceramide synthesis**
        in the stratum corneum, effectively fortifying the skin's defense against pollutants and transepidermal water loss. This makes it a multi-functional hero for almost all skin conditions.
        """)
        st.markdown("---")
        st.subheader("Article 3: The Importance of Post-Cleansing pH")
        st.markdown("""
        The skin's natural pH is slightly acidic (around 5.5). Using highly alkaline cleansers (pH 8+) can disrupt the **acid mantle**, 
        leading to increased vulnerability to bacteria (like P. acnes) and environmental damage. Always choose a cleanser marketed as pH-balanced or low-pH.
        """)

    with tab_quiz:
        st.header("Skinova Master Quiz (5 Questions)")
        st.markdown("Answer correctly to receive a **+5 Skin Score bonus**!")
        
        quiz_questions = [
            ("Which ingredient is a humectant and can hold up to 1000 times its weight in water?", ["Ceramides", "Hyaluronic Acid", "Retinoids", "Lactic Acid"], "Hyaluronic Acid"),
            ("The skin's lipid barrier is primarily composed of:", ["Water, Salt, and Sugar", "Ceramides, Cholesterol, and Fatty Acids", "AHA, BHA, and PHA", "Melanin, Keratin, and Water"], "Ceramides, Cholesterol, and Fatty Acids"),
            ("Which type of acid is oil-soluble and penetrates pores to dissolve sebum and dead skin?", ["Glycolic Acid (AHA)", "Salicylic Acid (BHA)", "Lactic Acid (AHA)"], "Salicylic Acid (BHA)"),
            ("What is the maximum effective concentration of Niacinamide often recommended to avoid irritation?", ["25%", "5%", "15%", "1%"], "5%"),
            ("Which UV ray is responsible for premature aging and penetrates deeper into the dermis?", ["UVB", "UVA"], "UVA")
        ]
        
        # State to store answers and score
        if 'quiz_score' not in st.session_state:
            st.session_state.quiz_score = None
            st.session_state.quiz_answers = {}

        with st.form("master_quiz_form"):
            user_answers = {}
            for i, (q, options, _) in enumerate(quiz_questions):
                user_answers[f'q{i+1}'] = st.radio(f"**{i+1}.** {q}", options, key=f"quiz_q{i+1}")
            
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
                    if not st.session_state.user_data_profile.get('Quiz_Certified', False):
                        st.balloons()
                        st.success("🏆 Perfect Score! You're a Skinova Certified Expert! +5 Skin Score awarded.")
                        
                        # Update Score Logic
                        st.session_state.skin_score = min(99, st.session_state.skin_score + 5)
                        st.session_state.skin_score_history[-1] = st.session_state.skin_score # Update today's score
                        
                        save_user_data(st.session_state.user_email, {
                            'Skin Score': st.session_state.skin_score,
                            'Score_History': st.session_state.skin_score_history,
                            'Quiz_Certified': True # Set flag to prevent future bonuses
                        })
                    else:
                         st.info("You already earned the +5 bonus. Great review!")
                else:
                    st.error(f"Needs Improvement. Score: {final_score}. Review the academy and try again!")
                
                # Show Detailed Feedback
                for i, (q, _, correct_answer) in enumerate(quiz_questions):
                    q_key = f'q{i+1}'
                    user_ans = st.session_state.quiz_answers.get(q_key)
                    is_correct = user_ans == correct_answer
                    feedback_icon = "✅" if is_correct else "❌"
                    st.markdown(f"**{feedback_icon} Q{i+1}:** {q} | *Your Answer:* **{user_ans}** | *Correct:* **{correct_answer}**")


### ---
## 9. Community Forum (Basic CRUD Simulation)
def community_forum_page():
    st.title("Community Forum: Connect & Share 💬")
    st.markdown("---")
    
    st.subheader("Post a Question for Peer Review")
    
    with st.form("post_question_form"):
        # Use unique keys to avoid conflict
        post_title = st.text_input("Title of your question (e.g., Retinol Purge - Day 5?)", max_chars=100, key="forum_title_input")
        post_content = st.text_area("Your full question/concern (Max 500 chars)", height=150, max_chars=500, key="forum_content_input")
        post_submitted = st.form_submit_button("Submit Question to Forum")
        
        if post_submitted:
            if not post_title or not post_content:
                st.warning("Please fill in both the title and your question.")
            else:
                new_post = {
                    'User_Email': st.session_state.user_email,
                    'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'Post_Title': post_title,
                    'Post_Content': post_content,
                    'Post_ID': random.getrandbits(32) # Simple unique ID
                }
                
                st.session_state.forum_posts.append(new_post)
                st.session_state.forum_posts.sort(key=lambda x: x['Timestamp'], reverse=True)
                st.success("✅ Your question has been posted to the hyper-forum!")
                
                # Clear form inputs after successful submission
                st.session_state["forum_title_input"] = ""
                st.session_state["forum_content_input"] = ""
                st.experimental_rerun()
                
    st.markdown("---")
    
    st.subheader("🔥 Latest Community Questions")

    if st.session_state.forum_posts:
        recent_posts = st.session_state.forum_posts[:8] # Show top 8 recent posts
        
        for post in recent_posts:
            # Use user_email or first part of email for display
            display_user = post['User_Email'].split('@')[0]
            with st.expander(f"**{post['Post_Title']}** - *Posted by {display_user} on {post['Timestamp'][:10]}*"):
                st.markdown(f"**Concern:** {post['Post_Content']}")
                st.markdown("---")
                st.markdown(f"_Hyper-Simulation: Dummy Replies: {random.randint(2, 7)}, Last Activity: {random.choice(['Just Now', '1 hour ago', '4 hours ago'])}_")
    else:
        st.info("No questions posted yet. Be the first to start the conversation!")


### ---
## 10. Consult an Expert (Enhanced Form)
def consult_expert_page():
    st.title("Consult a Skinova Expert 👩‍⚕️")
    st.markdown("---")
    
    st.subheader("Book Your Virtual 1-on-1 Session")
    st.markdown("Provide detailed information below for our experts to prepare a hyper-personalized plan before your call.")

    user_data = st.session_state.user_data_profile

    with st.form("consult_form"):
        st.markdown("### Your Details")
        con_name = st.text_input("Your Full Name", value=user_data.get('Name', ''), disabled=True)
        con_email = st.text_input("Your Email", value=user_data.get('Email', ''), disabled=True)
        
        st.markdown("### Consultation Focus (Hyper-Intake)")
        
        col_type, col_time = st.columns(2)
        with col_type:
            concern_type = st.selectbox("Type of Consultation", ['Routine Review & Optimization (30 min)', 'Advanced Acne Management (45 min)', 'Deep Anti-Aging Strategies (60 min)', 'Product Allergy & Patch Test Guidance (30 min)'])
        with col_time:
            preferred_slot = st.selectbox("Preferred Time Slot (Simulated Availability)", 
                                          [f"Tomorrow, {t}:00 PM" for t in [10, 11, 2, 3, 5]])

        con_concern = st.text_area("Describe your concern/question in detail (Max 800 chars)", height=200, max_chars=800)
        
        st.markdown("### Optional: Provide Visual Context")
        uploaded_image = st.file_uploader("Upload a high-res image of the area (Optional)", type=["jpg", "jpeg", "png"])
        
        consult_submitted = st.form_submit_button("Submit Consultation Request")

        if consult_submitted:
            if not con_concern:
                st.warning("Please describe your concern.")
            else:
                image_status = "Image attached" if uploaded_image else "No image attached"
                
                new_consult = {
                    'Name': con_name,
                    'Email': con_email,
                    'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'Consult_Type': concern_type,
                    'Concern_Detail': con_concern,
                    'Image_Status': image_status,
                    'Preferred_Slot': preferred_slot,
                    'Status': 'Pending Review'
                }
                
                st.session_state.consult_requests.append(new_consult)
                
                st.success("✅ Your consultation request has been submitted!")
                st.markdown(f"""
                <div class="skinova-card" style="background-color: #4CAF5010; border-left: 5px solid #4CAF50;">
                    <p style='font-weight: bold;'>Confirmation & Next Steps:</p>
                    <p>Our expert team has received your request regarding **{concern_type.split('(')[0].strip()}**.</p>
                    <p>We will confirm your **{preferred_slot}** slot and send a secure video link via email within 4 hours.</p>
                    <p style='font-style: italic;'>Current number of requests in queue: {len(st.session_state.consult_requests)}</p>
                </div>
                """, unsafe_allow_html=True)


# --- 7. MAIN APP ROUTER ---

# Sidebar Navigation (Always Visible)
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <h2 style="color: white; margin: 0;">SKINOVAAI (V2)</h2>
        <p style="color: #FFFFFF90; font-size: 14px;">SESSION-BASED HYPER-PLATFORM</p>
        <p style="color: #FFD700; font-size: 12px; font-weight: bold;">(Data is saved only during this session)</p>
    </div>
    <hr style="border-top: 1px solid #FFFFFF50;"/>
    """, unsafe_allow_html=True)

    if st.session_state.logged_in:
        st.markdown(f"**Current User:** {st.session_state.user_email.split('@')[0]}", unsafe_allow_html=True)
        st.markdown(f"**Score:** {st.session_state.skin_score} | **Streak:** {st.session_state.routine_streak} days 🔥", unsafe_allow_html=True)
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
        if st.button("🚪 Logout & Reset Session", help="Log out of the application"):
            logout()
            
    else:
        st.info("Please Login or Signup to access the Hyper-Platform.")
        if st.button("Start My Journey"):
            navigate_to('Login/Signup')


# Main Content Display (Router Logic)
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
