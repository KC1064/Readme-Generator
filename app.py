import streamlit as st

from config import load_api_keys
from github_utils import extract_repo_info, fetch_repo_data
from gemini_utils import initialize_gemini, generate_readme


st.set_page_config(page_title="GitHub README Generator", layout="wide")
st.title("GitHub README Generator")

st.write("Generate professional README.md files for GitHub repositories using AI")


api_key = load_api_keys() 

with st.sidebar:
    st.header("Configuration")
    if api_key:
        st.success("Gemini API key loaded from .env")
    else:
        st.warning("Gemini API key not found in .env file. Please add API_KEY='YOUR_KEY' to a .env file.")
        # Option to let user input if .env is missing
        api_key = st.text_input("Enter Gemini API Key (if not in .env)", type="password")


    github_token = st.text_input(
        "GitHub Token (Optional)",
        type="password",
        help="Provide a GitHub token to increase API rate limits and access private repositories. Create one in GitHub Settings > Developer settings > Personal access tokens."
    )

st.markdown("---")
st.markdown("### How to use")
st.markdown("""
1.  Ensure you have a `.env` file in the same directory as the script with your `API_KEY` (or enter it in the sidebar).
2.  Paste a public or private GitHub repository URL.
3.  If it's a private repository, enter a GitHub Personal Access Token with `repo` scope.
4.  Click 'Generate README'.
5.  Copy the generated README or download it.
""")
st.markdown("---")


repo_url = st.text_input("GitHub Repository URL", help="Enter the full URL of the GitHub repository (e.g., `https://github.com/username/repository`)")


if st.button("Generate README"):
    # Check if API key is available (either from .env or input)
    if not api_key:
        st.error("Please provide a Gemini API key.")
        st.stop() # Stop execution

    if not repo_url:
        st.error("Please enter a GitHub repository URL.")
        st.stop() # Stop execution

    try:
        # --- Initialize Gemini Model ---
        model = initialize_gemini(api_key)
        if not model:
            st.error("Failed to initialize Gemini model. Cannot proceed.")
            st.stop()

        # --- Extract Repo Info ---
        username, repo_name = extract_repo_info(repo_url)
        st.info(f"Analyzing repository: {username}/{repo_name}")

        # --- Fetch Repository Data ---
        repo_data = fetch_repo_data(username, repo_name, github_token)

        if repo_data:
            # --- Generate README ---
            readme_content = generate_readme(model, repo_data)

            if readme_content:
                st.subheader("Generated README")
                st.markdown(readme_content)

                st.markdown("---") 

                # 2. Display the download button
                st.download_button(
                    label="Download README.md",
                    data=readme_content,
                    file_name="README.md",
                    mime="text/markdown",
                )
                

                


    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        st.exception(e) # Display traceback in Streamlit console for debugging

st.markdown("---")
st.markdown("Made with ❤️ for Developers")