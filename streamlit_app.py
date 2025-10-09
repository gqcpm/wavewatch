"""
WaveWatch - Surf Conditions App
A simple Streamlit app to get surf conditions for any beach.
"""

import streamlit as st
import os
from dotenv import load_dotenv
from src.wavewatch.llm.summarizer import SurfSummarizer

# Load environment variables from .env file
load_dotenv()

# Configure page
st.set_page_config(
    page_title="WaveWatch",
    page_icon="🏄‍♂️",
    layout="wide"
)

def main():
    """Main Streamlit app function."""
    
    # Get API key from environment
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        st.error("GEMINI_API_KEY not found in environment variables. Please check your .env file.")
        st.stop()
    
    # Header
    st.title("🏄‍♂️ WaveWatch")
    st.subheader("Get surf conditions for any beach")
    
    # Main content area
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("Beach Input")
        surf_beach = st.text_input(
            "Enter surf beach name:",
            placeholder="e.g., Pleasure Point, Malibu, Pipeline",
            help="Enter the name of the surf break you want to check"
        )
        
        if st.button("Get Surf Conditions", type="primary"):
            if not surf_beach:
                st.error("Please enter a beach name.")
            else:
                with st.spinner("Analyzing surf conditions..."):
                    try:
                        summarizer = SurfSummarizer(api_key=api_key)
                        conditions = summarizer.get_surf_conditions(surf_beach)
                        
                        # Store in session state for display
                        st.session_state.conditions = conditions
                        st.session_state.beach = surf_beach
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    with col2:
        st.header("Surf Conditions")
        
        if hasattr(st.session_state, 'conditions') and st.session_state.conditions:
            st.subheader(f"Conditions for {st.session_state.beach}")
            
            # Display the conditions with nice formatting
            st.markdown("---")
            st.markdown(st.session_state.conditions)
            
            # Add a download button for the conditions
            st.download_button(
                label="Download Conditions Report",
                data=st.session_state.conditions,
                file_name=f"{st.session_state.beach.replace(' ', '_')}_conditions.txt",
                mime="text/plain"
            )
        else:
            st.info("Enter a beach name and click 'Get Surf Conditions' to see the analysis.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**WaveWatch** - Powered by Google Gemini AI | "
        "Get your API key at [Google AI Studio](https://makersuite.google.com/app/apikey)"
    )

if __name__ == "__main__":
    main()
