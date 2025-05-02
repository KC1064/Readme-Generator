import google.generativeai as genai
from google.generativeai import GenerativeModel
import streamlit as st # 

def initialize_gemini(api_key):
    """Initializes the Gemini model."""
    if not api_key:
        st.error("No API key provided. Please check your .env file or input.")
        return None
    try:
        genai.configure(api_key=api_key)
       
        model = GenerativeModel('gemini-2.0-flash')

        st.success("Successfully initialized Gemini model")
        return model
    except Exception as e:
        st.error(f"Error initializing Gemini model. Check your API key and network connection: {e}")
        return None

def generate_readme(model, repo_data):
    """Generates a professional README using the Gemini model."""
    if model is None:
        st.error("AI model not initialized.")
        return None


    repo_info = repo_data.get('repo_info', {})
    languages = repo_data.get('languages', {})
    recent_commits = repo_data.get('recent_commits', [])
    frameworks = repo_data.get('frameworks', [])
    tech_stack_dict = repo_data.get('tech_stack', {}) 

    repo_name = repo_info.get('name', 'Unknown Repository')
    repo_description = repo_info.get('description') or 'No description provided'
    language_list = list(languages.keys())[:3] if languages else ['Unknown']
    topics = repo_info.get('topics', []) or ['None specified']
    created_at = repo_info.get('created_at', 'Unknown')
    updated_at = repo_info.get('updated_at', 'Unknown')

    license_info = repo_info.get('license')
    license_name = license_info.get('name', 'the project\'s license') if isinstance(license_info, dict) else 'the project\'s license'


    commit_messages = []
    if isinstance(recent_commits, list):
        for commit in recent_commits:
            if commit and isinstance(commit, dict) and 'commit' in commit:
                message = commit['commit'].get('message', '')
                if message:
                    commit_messages.append('- ' + message.split('\n')[0])

    if not commit_messages:
        commit_messages = ['- No recent commits found']


    # Format tech stack from the dictionary structure {Category: [(name, version), ...]}
    tech_stack_section = []
    if tech_stack_dict:
        for category, items in tech_stack_dict.items():
            tech_stack_section.append(f"**{category}**")
            if items:
                 for name, version in items:
                     tech_stack_section.append(f"- {name} (v{version})" if version else f"- {name}")
            else:
                tech_stack_section.append("  _No specific items detected in this category._")
    elif frameworks: # Fallback if structured tech_stack is empty but frameworks list exists
        tech_stack_section = ["**Key Technologies**"]
        for framework in frameworks:
            tech_stack_section.append(f"- {framework}")


    tech_stack_text = "\n".join(tech_stack_section) if tech_stack_section else "No specific tech stack detected"

    
    raw_dependency_contents = repo_data.get('raw_dependency_contents', {})

    dependency_info_for_prompt = []
    important_files_keywords = ["package.json", "requirements.txt", "pom.xml", "build.gradle", "go.mod", "Cargo.toml"]


    for file_path, content in raw_dependency_contents.items():
         if any(keyword in file_path.lower() for keyword in important_files_keywords):
             content_preview = content[:500] + "\n..." if len(content) > 500 else content
             dependency_info_for_prompt.append(f"File: `{file_path}`\n```\n{content_preview}\n```")

    
    if len(dependency_info_for_prompt) < 3:
         for file_path, content in raw_dependency_contents.items():
             if not any(keyword in file_path.lower() for keyword in important_files_keywords):
                 content_preview = content[:300] + "\n..." if len(content) > 300 else content
                 dependency_info_for_prompt.append(f"File: `{file_path}`\n```\n{content_preview}\n```")

    dependency_section_text = "\n\n".join(dependency_info_for_prompt) if dependency_info_for_prompt else "No dependency files found or contents could not be fetched."


    # System Prompt
    prompt = f"""
    You are a professional technical writer tasked with creating a comprehensive, well-structured README.md file for a GitHub repository.

    Repository Information:
    - Name: {repo_name}
    - Description: {repo_description}
    - Primary languages: {', '.join(language_list)}
    - Topics: {', '.join(topics)}
    - Created: {created_at}
    - Last update: {updated_at}

    Recent commit messages (provide context for features/recent work):
    {chr(10).join(commit_messages)}

    Detected Technology Stack:
    {tech_stack_text}

    Relevant Dependency/Configuration File Contents (for installation/tech context):
    {dependency_section_text}

    Based on this information, create a professional README.md file that includes:
    1.  A clear title (Repo Name) and concise description of the project.
    2.  A comprehensive Tech Stack section using the 'Detected Technology Stack' info, organized by category.
    3.  Installation instructions. Infer steps from languages, tech stack, and dependency files (e.g., `npm install`, `pip install`, `mvn clean install`). Provide general steps if specific ones aren't clear.
    4.  Usage examples. Make reasonable assumptions based on description, commits, and tech stack.
    5.  A Features section. Infer key features or capabilities from the description, topics, tech stack, and recent commit messages.
    6.  Contribution guidelines (standard placeholder).
    7.  License information (use "{license_name}").
    8.  A well-organized structure with proper Markdown formatting (headers, code blocks, lists, etc.).

    The README should be comprehensive yet concise. Add relevant emojis where needed to make it eye-catching and professional.

    Format the output *only* as clean Markdown suitable for a README.md file. Do not include any introductory or concluding remarks outside the README content itself.
    """

    with st.spinner("Generating README with AI..."):
        try:
            response = model.generate_content(prompt)
            readme_text = response.text
             
            if not readme_text.strip().startswith('#'):
                readme_text = f"# {repo_name}\n\n" + readme_text
            return readme_text
        except Exception as e:
            st.error(f"Error generating README content with AI: {e}")
            st.exception(e) # Show traceback in Streamlit console
            return None