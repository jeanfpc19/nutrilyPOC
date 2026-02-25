import streamlit as st
import google.generativeai as genai

# 1. Configuration
# API Key handling (best practice is using st.secrets for deployment)
# genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.title("Nutritionist AI Companion")

# Initialize Session State to store the diet plan across the session
if "diet_plan" not in st.session_state:
    st.session_state["diet_plan"] = ""

# 2. Sidebar for Navigation
role = st.sidebar.radio("Select User Type:", ["Nutritionist", "Patient"])

# --- NUTRITIONIST VIEW ---
if role == "Nutritionist":
    st.header("Upload Patient Plan")
    diet_input = st.text_area("Paste diet plan, restrictions, and macros here:")
    
    if st.button("Save Plan"):
        st.session_state["diet_plan"] = diet_input
        st.success("Plan loaded successfully! Switch to 'Patient' view to test.")

# --- PATIENT VIEW ---
elif role == "Patient":
    st.header("Chat with your Assistant")
    
    # Check if a plan exists
    if not st.session_state["diet_plan"]:
        st.warning("No diet plan found. Please have the nutritionist load the data first.")
    else:
        user_question = st.text_input("Ask about your diet:")
        
        if user_question:
            # 3. The RAG Logic (Simple Prompt Stuffing)
            prompt = f"""
            You are a strict nutritionist assistant. 
            Here is the patient's specific profile and restrictions:
            {st.session_state['diet_plan']}
            
            Patient Question: {user_question}
            
            Answer the question strictly based on the profile above. 
            If the food is not allowed or contradicts the macros, say no.
            """
            
            # Call the LLM (Gemini)
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            
            st.write(response.text)
