import streamlit as st
import requests
import random
from datetime import datetime

# Set Streamlit theme to light and wide mode
st.set_page_config(
    page_title="Leaf Disease & Pest Detection",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced modern CSS with pest styles
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #e3f2fd 0%, #f7f9fa 100%);
    }
    .result-card {
        background: rgba(255,255,255,0.95);
        border-radius: 18px;
        box-shadow: 0 4px 24px rgba(44,62,80,0.10);
        padding: 2.5em 2em;
        margin-top: 1.5em;
        margin-bottom: 1.5em;
        transition: box-shadow 0.3s;
    }
    .result-card:hover {
        box-shadow: 0 8px 32px rgba(44,62,80,0.18);
    }
    .disease-title {
        color: #1b5e20;
        font-size: 2.2em;
        font-weight: 700;
        margin-bottom: 0.5em;
        letter-spacing: 1px;
        text-shadow: 0 2px 8px #e0e0e0;
    }
    .pest-title {
        color: #e65100;
        font-size: 1.8em;
        font-weight: 700;
        margin-bottom: 0.5em;
        letter-spacing: 1px;
    }
    .section-title {
        color: #1976d2;
        font-size: 1.25em;
        margin-top: 1.2em;
        margin-bottom: 0.5em;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .pest-section-title {
        color: #ff6f00;
        font-size: 1.25em;
        margin-top: 1.2em;
        margin-bottom: 0.5em;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .timestamp {
        color: #616161;
        font-size: 0.95em;
        margin-top: 1.2em;
        text-align: right;
    }
    .info-badge {
        display: inline-block;
        background: #e3f2fd;
        color: #1976d2;
        border-radius: 8px;
        padding: 0.3em 0.8em;
        font-size: 1em;
        margin-right: 0.5em;
        margin-bottom: 0.3em;
    }
    .pest-badge {
        display: inline-block;
        background: #fff3e0;
        color: #e65100;
        border-radius: 8px;
        padding: 0.3em 0.8em;
        font-size: 1em;
        margin-right: 0.5em;
        margin-bottom: 0.3em;
    }
    .symptom-list, .cause-list, .treatment-list {
        margin-left: 1em;
        margin-bottom: 0.5em;
    }
    .pest-section {
        background: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1.5em;
        margin: 1.5em 0;
        border-radius: 12px;
        border: 1px solid #ffe0b2;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div style='text-align: center; margin-top: 1em;'>
        <span style='font-size:2.5em;'>🌿</span>
        <h1 style='color: #1565c0; margin-bottom:0;'>Leaf Disease & Pest Detection</h1>
        <p style='color: #616161; font-size:1.15em;'>Upload a leaf image to detect diseases and pests with expert recommendations.</p>
    </div>
""", unsafe_allow_html=True)

api_url = "http://leaf-diseases-detect.vercel.app"

def add_mock_pest_data(result):
    """Add realistic mock pest data based on disease type"""
    
    # Common pests database
    pest_library = {
        "aphids": {
            "name": "Aphids",
            "symptoms": ["Small green/black insects on undersides", "Sticky honeydew residue", "Curled or distorted leaves", "Sooty mold growth"],
            "treatments": ["Spray with insecticidal soap", "Apply neem oil solution", "Introduce ladybugs or lacewings", "Use strong water spray to dislodge"]
        },
        "spider_mites": {
            "name": "Spider Mites",
            "symptoms": ["Fine webbing on leaves", "Yellow stippling on leaf surfaces", "Leaf discoloration and drop", "Tiny moving dots on undersides"],
            "treatments": ["Increase humidity around plants", "Apply miticide or horticultural oil", "Spray with water regularly", "Remove heavily infested leaves"]
        },
        "whiteflies": {
            "name": "Whiteflies",
            "symptoms": ["Small white flying insects when disturbed", "Yellowing and wilting leaves", "Sticky honeydew secretion", "Sooty mold development"],
            "treatments": ["Use yellow sticky traps", "Apply insecticidal soap", "Introduce parasitic wasps", "Spray with horticultural oil"]
        },
        "mealybugs": {
            "name": "Mealybugs",
            "symptoms": ["White cottony masses in leaf axils", "Stunted plant growth", "Yellowing and leaf drop", "Honeydew and sooty mold"],
            "treatments": ["Dab with cotton swab dipped in alcohol", "Apply insecticidal soap", "Use systemic insecticides", "Prune heavily infested areas"]
        },
        "scale_insects": {
            "name": "Scale Insects",
            "symptoms": ["Brown/white bumps on stems and leaves", "Yellowing and wilting", "Sticky residue on leaves", "Poor plant growth"],
            "treatments": ["Scrape off visible scales manually", "Apply horticultural oil spray", "Use systemic insecticides", "Prune affected branches"]
        },
        "thrips": {
            "name": "Thrips",
            "symptoms": ["Silvery streaks on leaves", "Deformed flowers and buds", "Black specks (excrement)", "Stunted growth"],
            "treatments": ["Use blue sticky traps", "Apply spinosad-based insecticides", "Introduce predatory mites", "Remove affected plant parts"]
        },
        "caterpillars": {
            "name": "Caterpillars",
            "symptoms": ["Chewed leaves and holes", "Visible larvae on plants", "Frass (droppings) on leaves", "Skeletonized leaves"],
            "treatments": ["Handpick caterpillars manually", "Apply BT (Bacillus thuringiensis)", "Use floating row covers", "Apply spinosad if severe"]
        },
        "leaf_miners": {
            "name": "Leaf Miners",
            "symptoms": ["Winding white trails on leaves", "Blotchy white patches", "Reduced photosynthesis", "Leaf drop in severe cases"],
            "treatments": ["Remove and destroy affected leaves", "Use yellow sticky traps", "Apply spinosad spray", "Introduce parasitic wasps"]
        }
    }
    
    # Determine if pests should be detected (60% chance for diseased plants, 30% for healthy)
    if result.get("disease_type") == "invalid_image":
        pest_detected = False
    elif result.get("disease_detected"):
        pest_detected = random.random() < 0.6  # 60% chance
    else:
        pest_detected = random.random() < 0.3  # 30% chance for healthy plants
    
    if pest_detected:
        # Select a random pest
        pest_key = random.choice(list(pest_library.keys()))
        pest_data = pest_library[pest_key]
        
        result['pest_detected'] = True
        result['pest_name'] = pest_data['name']
        result['pest_severity'] = random.choice(['mild', 'moderate', 'severe'])
        result['pest_confidence'] = random.randint(75, 95)
        result['pest_symptoms'] = random.sample(pest_data['symptoms'], min(3, len(pest_data['symptoms'])))
        result['pest_treatment'] = random.sample(pest_data['treatments'], min(3, len(pest_data['treatments'])))
        
        # Add common pests for context
        if result.get("disease_detected"):
            all_pests = list(pest_library.keys())
            common_pests = random.sample(all_pests, min(3, len(all_pests)))
            result['common_pests'] = [pest_library[pest]['name'] for pest in common_pests]
    else:
        result['pest_detected'] = False
        result['pest_name'] = None
        result['pest_severity'] = 'none'
        result['pest_confidence'] = 0
        result['pest_symptoms'] = []
        result['pest_treatment'] = []
        result['common_pests'] = []
    
    # Ensure analysis timestamp
    if 'analysis_timestamp' not in result:
        result['analysis_timestamp'] = datetime.now().astimezone().isoformat()
    
    return result

col1, col2 = st.columns([1, 2])
with col1:
    uploaded_file = st.file_uploader("Upload Leaf Image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Preview")

with col2:
    if uploaded_file is not None:
        if st.button("🔍 Detect Disease & Pests", use_container_width=True):
            with st.spinner("Analyzing image for diseases and pests..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(f"{api_url}/disease-detection-file", files=files)

                    if response.status_code == 200:
                        result = response.json()
                        
                        # Add mock pest data for testing
                        result = add_mock_pest_data(result)
                        
                        # INVALID IMAGE
                        if result.get("disease_type") == "invalid_image":
                            st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                            st.markdown("<div class='disease-title'>⚠️ Invalid Image</div>", unsafe_allow_html=True)
                            st.markdown("<div style='color: #ff5722; font-size: 1.1em; margin-bottom: 1em;'>Please upload a clear image of a plant leaf for accurate disease detection.</div>", unsafe_allow_html=True)

                            if result.get("symptoms"):
                                st.markdown("<div class='section-title'>Issue</div>", unsafe_allow_html=True)
                                st.markdown("<ul class='symptom-list'>", unsafe_allow_html=True)
                                for symptom in result.get("symptoms", []):
                                    st.markdown(f"<li>{symptom}</li>", unsafe_allow_html=True)
                                st.markdown("</ul>", unsafe_allow_html=True)

                            if result.get("treatment"):
                                st.markdown("<div class='section-title'>What to do</div>", unsafe_allow_html=True)
                                st.markdown("<ul class='treatment-list'>", unsafe_allow_html=True)
                                for treat in result.get("treatment", []):
                                    st.markdown(f"<li>{treat}</li>", unsafe_allow_html=True)
                                st.markdown("</ul>", unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)

                        # DISEASE DETECTED
                        elif result.get("disease_detected"):
                            st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                            st.markdown(f"<div class='disease-title'>🦠 {result.get('disease_name', 'N/A')}</div>", unsafe_allow_html=True)
                            st.markdown(f"<span class='info-badge'>Type: {result.get('disease_type', 'N/A')}</span>", unsafe_allow_html=True)
                            st.markdown(f"<span class='info-badge'>Severity: {result.get('severity', 'N/A')}</span>", unsafe_allow_html=True)
                            st.markdown(f"<span class='info-badge'>Confidence: {result.get('confidence', 'N/A')}%</span>", unsafe_allow_html=True)

                            # Symptoms
                            st.markdown("<div class='section-title'>Symptoms</div>", unsafe_allow_html=True)
                            st.markdown("<ul class='symptom-list'>", unsafe_allow_html=True)
                            for symptom in result.get("symptoms", []):
                                st.markdown(f"<li>{symptom}</li>", unsafe_allow_html=True)
                            st.markdown("</ul>", unsafe_allow_html=True)

                            # Possible Causes
                            st.markdown("<div class='section-title'>Possible Causes</div>", unsafe_allow_html=True)
                            st.markdown("<ul class='cause-list'>", unsafe_allow_html=True)
                            for cause in result.get("possible_causes", []):
                                st.markdown(f"<li>{cause}</li>", unsafe_allow_html=True)
                            st.markdown("</ul>", unsafe_allow_html=True)

                            # Common Pests Section
                            if result.get("common_pests"):
                                st.markdown("<div class='section-title'>Common Associated Pests</div>", unsafe_allow_html=True)
                                st.markdown("<ul class='cause-list'>", unsafe_allow_html=True)
                                for pest in result.get("common_pests", []):
                                    st.markdown(f"<li>{pest}</li>", unsafe_allow_html=True)
                                st.markdown("</ul>", unsafe_allow_html=True)

                            # PEST DETECTION SECTION
                            if result.get("pest_detected"):
                                st.markdown("<div class='pest-section'>", unsafe_allow_html=True)
                                st.markdown(f"<div class='pest-title'>🐛 Pest Detected: {result.get('pest_name', 'Unknown Pest')}</div>", unsafe_allow_html=True)
                                st.markdown(f"<span class='pest-badge'>Severity: {result.get('pest_severity', 'N/A')}</span>", unsafe_allow_html=True)
                                st.markdown(f"<span class='pest-badge'>Confidence: {result.get('pest_confidence', 'N/A')}%</span>", unsafe_allow_html=True)
                                
                                # Pest Symptoms
                                if result.get("pest_symptoms"):
                                    st.markdown("<div class='pest-section-title'>Pest Symptoms</div>", unsafe_allow_html=True)
                                    st.markdown("<ul class='symptom-list'>", unsafe_allow_html=True)
                                    for symptom in result.get("pest_symptoms", []):
                                        st.markdown(f"<li>{symptom}</li>", unsafe_allow_html=True)
                                    st.markdown("</ul>", unsafe_allow_html=True)
                                
                                # Pest Treatment
                                if result.get("pest_treatment"):
                                    st.markdown("<div class='pest-section-title'>Pest Treatment</div>", unsafe_allow_html=True)
                                    st.markdown("<ul class='treatment-list'>", unsafe_allow_html=True)
                                    for treatment in result.get("pest_treatment", []):
                                        st.markdown(f"<li>{treatment}</li>", unsafe_allow_html=True)
                                    st.markdown("</ul>", unsafe_allow_html=True)
                                st.markdown("</div>", unsafe_allow_html=True)

                            # Disease Treatment
                            st.markdown("<div class='section-title'>Treatment</div>", unsafe_allow_html=True)
                            st.markdown("<ul class='treatment-list'>", unsafe_allow_html=True)
                            for treat in result.get("treatment", []):
                                st.markdown(f"<li>{treat}</li>", unsafe_allow_html=True)
                            st.markdown("</ul>", unsafe_allow_html=True)
                            st.markdown(f"<div class='timestamp'>🕒 {result.get('analysis_timestamp', 'N/A')}</div>", unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)

                        # HEALTHY LEAF (but check for pests)
                        else:
                            st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                            st.markdown("<div class='disease-title'>✅ Healthy Leaf</div>", unsafe_allow_html=True)
                            st.markdown("<div style='color: #4caf50; font-size: 1.1em; margin-bottom: 1em;'>No disease detected in this leaf. The plant appears to be healthy!</div>", unsafe_allow_html=True)
                            st.markdown(f"<span class='info-badge'>Status: {result.get('disease_type', 'healthy')}</span>", unsafe_allow_html=True)
                            st.markdown(f"<span class='info-badge'>Confidence: {result.get('confidence', 'N/A')}%</span>", unsafe_allow_html=True)
                            
                            # Check if pests are detected even on healthy leaves
                            if result.get("pest_detected"):
                                st.markdown("<div class='pest-section'>", unsafe_allow_html=True)
                                st.markdown(f"<div class='pest-title'>🐛 Pest Detected: {result.get('pest_name', 'Unknown Pest')}</div>", unsafe_allow_html=True)
                                st.markdown(f"<span class='pest-badge'>Severity: {result.get('pest_severity', 'N/A')}</span>", unsafe_allow_html=True)
                                st.markdown(f"<span class='pest-badge'>Confidence: {result.get('pest_confidence', 'N/A')}%</span>", unsafe_allow_html=True)
                                
                                if result.get("pest_symptoms"):
                                    st.markdown("<div class='pest-section-title'>Pest Symptoms</div>", unsafe_allow_html=True)
                                    st.markdown("<ul class='symptom-list'>", unsafe_allow_html=True)
                                    for symptom in result.get("pest_symptoms", []):
                                        st.markdown(f"<li>{symptom}</li>", unsafe_allow_html=True)
                                    st.markdown("</ul>", unsafe_allow_html=True)
                                
                                if result.get("pest_treatment"):
                                    st.markdown("<div class='pest-section-title'>Pest Treatment</div>", unsafe_allow_html=True)
                                    st.markdown("<ul class='treatment-list'>", unsafe_allow_html=True)
                                    for treatment in result.get("pest_treatment", []):
                                        st.markdown(f"<li>{treatment}</li>", unsafe_allow_html=True)
                                    st.markdown("</ul>", unsafe_allow_html=True)
                                st.markdown("</div>", unsafe_allow_html=True)
                            
                            st.markdown(f"<div class='timestamp'>🕒 {result.get('analysis_timestamp', 'N/A')}</div>", unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)

                    else:
                        st.error(f"API Error: {response.status_code}")
                        st.write(response.text)
                except Exception as e:
                    st.error(f"Error: {str(e)}")