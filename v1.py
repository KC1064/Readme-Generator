import os
import streamlit as st
import requests
import json
import base64
from urllib.parse import urlparse
import google.generativeai as genai
from google.generativeai import GenerativeModel

st.set_page_config(page_title="GitHub README Generator", layout="wide")

# App title and description
st.title("GitHub README Generator")
st.write("Generate professional README.md files for GitHub repositories using AI")

# Sidebar for API keys
with st.sidebar:
    st.header("API Configuration")
    gemini_api_key = st.text_input("Gemini API Key", type="password", help="Enter your Google Gemini API key")
    github_token = st.text_input("GitHub Token (Optional)", type="password", 
                               help="GitHub token increases API rate limits and allows access to private repositories")
    
    st.markdown("---")
    st.markdown("### How to use")
    st.markdown("""
    1. Enter your Gemini API key
    2. Paste a GitHub repository URL
    3. Click 'Generate README'
    4. Copy the generated README or download it
    """)

# Initialize Gemini
def initialize_gemini(api_key):
    if not api_key:
        return None
    
    try:
        genai.configure(api_key=api_key)
        return GenerativeModel('gemini-1.5-pro')
    except Exception as e:
        st.error(f"Error initializing Gemini: {e}")
        return None

# Main form
repo_url = st.text_input("GitHub Repository URL", help="Enter the full URL of the GitHub repository")

def extract_repo_info(repo_url):
    """Extract username and repo name from GitHub URL"""
    parsed_url = urlparse(repo_url)
    path_parts = parsed_url.path.strip('/').split('/')
    
    if len(path_parts) >= 2:
        username = path_parts[0]
        repo_name = path_parts[1]
        return username, repo_name
    else:
        raise ValueError("Invalid GitHub repository URL format")

def get_file_content(username, repo_name, file_path, github_token=None):
    """Fetch the content of a specific file from the repository"""
    headers = {}
    if github_token:
        headers['Authorization'] = f'token {github_token}'
    
    content_url = f"https://api.github.com/repos/{username}/{repo_name}/contents/{file_path}"
    response = requests.get(content_url, headers=headers)
    
    if response.status_code == 200:
        content_data = response.json()
        if content_data.get('type') == 'file' and content_data.get('content'):
            try:
                decoded_content = base64.b64decode(content_data['content']).decode('utf-8')
                return decoded_content
            except Exception as e:
                st.warning(f"Error decoding content of {file_path}: {e}")
    
    return None

def find_files_recursively(username, repo_name, path="", target_files=None, github_token=None):
    """Recursively find target files in the repository"""
    if target_files is None:
        target_files = ["package.json"]
    
    found_files = []
    headers = {}
    if github_token:
        headers['Authorization'] = f'token {github_token}'
    
    contents_url = f"https://api.github.com/repos/{username}/{repo_name}/contents/{path}"
    response = requests.get(contents_url, headers=headers)
    
    if response.status_code != 200:
        st.warning(f"Could not access {path} in repository: {response.status_code}")
        return found_files
    
    contents = response.json()
    
    # Handle case where contents is not a list
    if not isinstance(contents, list):
        return found_files
    
    for item in contents:
        if item['type'] == 'file':
            for target in target_files:
                if item['name'] == target or item['name'].endswith(f"/{target}"):
                    found_files.append(item['path'])
        elif item['type'] == 'dir':
            # Skip certain directories that are commonly not relevant
            if any(skip in item['path'].lower() for skip in ['node_modules', 'vendor', 'dist', 'build']):
                continue
            # Recursive call for subdirectories
            found_files.extend(find_files_recursively(
                username, repo_name, item['path'], target_files, github_token
            ))
    
    return found_files

def parse_package_json(content):
    """Parse package.json content to extract dependencies and dev dependencies"""
    try:
        data = json.loads(content)
        dependencies = data.get('dependencies', {})
        dev_dependencies = data.get('devDependencies', {})
        return dependencies, dev_dependencies
    except json.JSONDecodeError:
        st.warning("Could not parse package.json content")
        return {}, {}

def extract_tech_stack_from_packages(dependencies, dev_dependencies):
    """Extract tech stack information from dependencies"""
    tech_stack = []
    
    # Common frontend frameworks
    frontend_frameworks = {
        'react': 'React',
        'vue': 'Vue.js',
        'angular': 'Angular',
        'svelte': 'Svelte',
        'next': 'Next.js',
        'nuxt': 'Nuxt.js',
        'gatsby': 'Gatsby',
    }
    
    # Common backend frameworks
    backend_frameworks = {
        'express': 'Express.js',
        'koa': 'Koa.js',
        'fastify': 'Fastify',
        'nest': 'NestJS',
        'apollo-server': 'Apollo Server',
        'graphql': 'GraphQL',
    }
    
    # UI libraries
    ui_libraries = {
        'material-ui': 'Material-UI',
        '@mui/material': 'Material-UI',
        'antd': 'Ant Design',
        'bootstrap': 'Bootstrap',
        'tailwindcss': 'Tailwind CSS',
        '@chakra-ui/react': 'Chakra UI',
        '@emotion': 'Emotion',
        'styled-components': 'Styled Components',
    }
    
    # State management
    state_management = {
        'redux': 'Redux',
        'mobx': 'MobX',
        'recoil': 'Recoil',
        'zustand': 'Zustand',
        '@reduxjs/toolkit': 'Redux Toolkit',
    }
    
    # Testing frameworks
    testing_frameworks = {
        'jest': 'Jest',
        'mocha': 'Mocha',
        'cypress': 'Cypress',
        '@testing-library/react': 'React Testing Library',
        'vitest': 'Vitest',
        'playwright': 'Playwright',
    }
    
    # Build tools
    build_tools = {
        'webpack': 'Webpack',
        'vite': 'Vite',
        'rollup': 'Rollup',
        'parcel': 'Parcel',
        'esbuild': 'esbuild',
        'babel': 'Babel',
        '@babel/core': 'Babel',
        'typescript': 'TypeScript',
    }
    
    # Check all dependencies
    all_deps = {**dependencies, **dev_dependencies}
    
    for dep, version in all_deps.items():
        dep_lower = dep.lower()
        
        # Check against all categories
        for category, lookup in [
            ('Frontend', frontend_frameworks),
            ('Backend', backend_frameworks),
            ('UI', ui_libraries),
            ('State Management', state_management),
            ('Testing', testing_frameworks),
            ('Build Tools', build_tools)
        ]:
            for key, name in lookup.items():
                if key.lower() in dep_lower:
                    tech_stack.append((category, name, version))
                    break
    
    return tech_stack

def identify_dependencies(username, repo_name, languages, github_token=None):
    """Identify frameworks and dependencies based on package files"""
    dependencies = {}
    frameworks = []
    tech_stack = {}
    
    # Files to check for dependencies based on language
    dependency_files = {
        'Python': ['requirements.txt', 'Pipfile', 'setup.py', 'pyproject.toml'],
        'JavaScript': ['package.json'],
        'TypeScript': ['package.json'],
        'Ruby': ['Gemfile'],
        'PHP': ['composer.json'],
        'Java': ['pom.xml', 'build.gradle'],
        'Go': ['go.mod'],
        'Rust': ['Cargo.toml'],
        'C#': ['*.csproj', 'packages.config'],
    }
    
    # Framework identifiers by file content
    framework_identifiers = {
        'Python': {
            'Django': ['django'],
            'Flask': ['flask'],
            'FastAPI': ['fastapi'],
            'Pandas': ['pandas'],
            'TensorFlow': ['tensorflow'],
            'PyTorch': ['torch'],
            'NumPy': ['numpy'],
            'Matplotlib': ['matplotlib'],
            'Scikit-learn': ['scikit-learn', 'sklearn'],
        },
        'JavaScript': {
            'React': ['react', 'react-dom'],
            'Vue.js': ['vue'],
            'Angular': ['@angular/core'],
            'Express': ['express'],
            'Next.js': ['next'],
            'Nuxt.js': ['nuxt'],
        },
        'Ruby': {
            'Rails': ['rails'],
            'Sinatra': ['sinatra'],
        },
        'PHP': {
            'Laravel': ['laravel/framework'],
            'Symfony': ['symfony/symfony'],
            'WordPress': ['wp-'],
        }
    }
    
    # Find all package.json files in the repo recursively
    if 'JavaScript' in languages or 'TypeScript' in languages or any('javascript' in lang.lower() for lang in languages):
        with st.spinner("Searching for package.json files recursively..."):
            package_files = find_files_recursively(username, repo_name, target_files=["package.json"], github_token=github_token)
            
            for file_path in package_files:
                content = get_file_content(username, repo_name, file_path, github_token)
                if content:
                    dependencies[file_path] = content
                    
                    # Parse the package.json content
                    main_deps, dev_deps = parse_package_json(content)
                    
                    # Extract tech stack information
                    stack_info = extract_tech_stack_from_packages(main_deps, dev_deps)
                    
                    # Organize by category
                    for category, name, version in stack_info:
                        if category not in tech_stack:
                            tech_stack[category] = []
                        tech_stack[category].append((name, version))
                        
                        # Add to frameworks as well for backward compatibility
                        if name not in frameworks:
                            frameworks.append(name)
    
    # Check other common dependency files
    for language, files in dependency_files.items():
        if language in languages or language.lower() in map(str.lower, languages):
            if language != 'JavaScript' and language != 'TypeScript':  # Already handled JS/TS above
                for file_name in files:
                    content = get_file_content(username, repo_name, file_name, github_token)
                    if content:
                        dependencies[file_name] = content
                        
                        # Identify frameworks based on content
                        if language in framework_identifiers:
                            for framework, keywords in framework_identifiers[language].items():
                                if any(keyword.lower() in content.lower() for keyword in keywords):
                                    frameworks.append(framework)
    
    # Check for special cases (frameworks with distinctive files)
    special_framework_files = {
        'angular.json': 'Angular',
        '.vue': 'Vue.js',
        'next.config.js': 'Next.js',
        'nuxt.config.js': 'Nuxt.js',
        'manage.py': 'Django',
        'webpack.config.js': 'webpack',
        'vite.config.js': 'Vite',
        'tailwind.config.js': 'Tailwind CSS',
        'jest.config.js': 'Jest',
        '.eslintrc': 'ESLint',
    }
    
    # Get repository contents
    try:
        headers = {}
        if github_token:
            headers['Authorization'] = f'token {github_token}'
        
        contents_url = f"https://api.github.com/repos/{username}/{repo_name}/contents"
        contents_response = requests.get(contents_url, headers=headers)
        contents_response.raise_for_status()
        
        contents = contents_response.json()
        for item in contents:
            if item['type'] == 'file':
                file_name = item['name']
                for special_file, framework_name in special_framework_files.items():
                    if special_file in file_name and framework_name not in frameworks:
                        frameworks.append(framework_name)
    except Exception as e:
        st.warning(f"Could not analyze repository contents: {e}")
    
    return {
        'dependencies': dependencies,
        'frameworks': list(set(frameworks)),  # Remove duplicates
        'tech_stack': tech_stack
    }

def fetch_repo_data(username, repo_name, github_token=None):
    """Fetch repository data from GitHub API"""
    headers = {}
    if github_token:
        headers['Authorization'] = f'token {github_token}'
    
    progress_bar = st.progress(0)
    progress_text = st.empty()
    
    # Fetch basic repo info
    progress_text.text("Fetching repository information...")
    repo_url = f"https://api.github.com/repos/{username}/{repo_name}"
    try:
        repo_response = requests.get(repo_url, headers=headers)
        repo_response.raise_for_status()
        repo_data = repo_response.json()
        progress_bar.progress(20)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            st.error(f"Repository not found: {username}/{repo_name}. Please check the URL.")
        elif e.response.status_code == 401 or e.response.status_code == 403:
            st.error("Authentication error. Please check your GitHub token or try again later.")
        else:
            st.error(f"Error fetching repository information: {e}")
        return None
    
    # Fetch languages used
    progress_text.text("Analyzing languages...")
    langs_url = f"https://api.github.com/repos/{username}/{repo_name}/languages"
    try:
        langs_response = requests.get(langs_url, headers=headers)
        langs_response.raise_for_status()
        languages = langs_response.json()
        progress_bar.progress(40)
    except requests.exceptions.HTTPError as e:
        st.warning(f"Could not fetch language information: {e}")
        languages = {}
    
    # Fetch latest commits
    progress_text.text("Fetching recent commits...")
    commits_url = f"https://api.github.com/repos/{username}/{repo_name}/commits?per_page=5"
    try:
        commits_response = requests.get(commits_url, headers=headers)
        commits_response.raise_for_status()
        commits = commits_response.json()
        progress_bar.progress(60)
    except requests.exceptions.HTTPError as e:
        st.warning(f"Could not fetch commits: {e}")
        commits = []
    
    # Try to get README if exists (for context)
    progress_text.text("Looking for existing README...")
    try:
        readme_url = f"https://api.github.com/repos/{username}/{repo_name}/readme"
        readme_response = requests.get(readme_url, headers=headers)
        readme_response.raise_for_status()
        readme_data = readme_response.json()
        readme_content = base64.b64decode(readme_data['content']).decode('utf-8')
    except:
        readme_content = "No README found"
    progress_bar.progress(70)
    
    # Identify frameworks and dependencies
    progress_text.text("Identifying frameworks and dependencies...")
    dependency_info = identify_dependencies(username, repo_name, list(languages.keys()), github_token)
    progress_bar.progress(100)
    progress_text.empty()
    
    return {
        "repo_info": repo_data,
        "languages": languages,
        "recent_commits": commits[:5] if isinstance(commits, list) else [],
        "existing_readme": readme_content,
        "frameworks": dependency_info['frameworks'],
        "dependencies": dependency_info['dependencies'],
        "tech_stack": dependency_info['tech_stack']
    }

def generate_readme(model, repo_data):
    """Generate a professional README using Gemini"""
    
    # Safety checks for None values
    repo_info = repo_data.get('repo_info', {}) or {}
    languages = repo_data.get('languages', {}) or {}
    recent_commits = repo_data.get('recent_commits', []) or []
    frameworks = repo_data.get('frameworks', []) or []
    dependencies = repo_data.get('dependencies', {}) or {}
    tech_stack = repo_data.get('tech_stack', {}) or {}
    
    # Extract information safely with fallbacks
    repo_name = repo_info.get('name', 'Unknown Repository')
    repo_description = repo_info.get('description') or 'No description provided'
    language_list = list(languages.keys())[:3] if languages else ['Unknown']
    topics = repo_info.get('topics', []) or ['None specified']
    created_at = repo_info.get('created_at', 'Unknown')
    updated_at = repo_info.get('updated_at', 'Unknown')
    
    # Safely extract license info
    license_info = repo_info.get('license') or {}
    license_name = license_info.get('name', 'the project\'s license') if isinstance(license_info, dict) else 'the project\'s license'
    
    # Safely extract commit messages
    commit_messages = []
    for commit in recent_commits:
        if commit and isinstance(commit, dict) and 'commit' in commit:
            message = commit['commit'].get('message', '')
            if message:
                commit_messages.append('- ' + message.split('\n')[0])
    
    if not commit_messages:
        commit_messages = ['- No recent commits found']
    
    # Format tech stack information
    tech_stack_section = []
    for category, items in tech_stack.items():
        tech_stack_section.append(f"{category}:")
        for name, version in items:
            tech_stack_section.append(f"- {name} ({version})")
    
    # If no tech stack was found, use the frameworks list
    if not tech_stack_section and frameworks:
        tech_stack_section = ["Key Technologies:"]
        for framework in frameworks:
            tech_stack_section.append(f"- {framework}")
    
    tech_stack_text = "\n".join(tech_stack_section) if tech_stack_section else "No specific tech stack detected"
    
    # Format dependency information for the prompt (limit to most important files)
    dependency_info = []
    important_files = ["package.json", "requirements.txt", "pom.xml", "build.gradle", "go.mod", "Cargo.toml"]
    
    # First add important dependency files
    for file_name, content in dependencies.items():
        if any(important in file_name for important in important_files):
            # Limit content length to avoid prompt size issues
            content_preview = content[:500] + "..." if len(content) > 500 else content
            dependency_info.append(f"File: {file_name}\n```\n{content_preview}\n```")
    
    # Then add any remaining files if we have space
    if len(dependency_info) < 3:  # Limit to avoid making prompt too large
        for file_name, content in dependencies.items():
            if not any(important in file_name for important in important_files):
                content_preview = content[:300] + "..." if len(content) > 300 else content
                dependency_info.append(f"File: {file_name}\n```\n{content_preview}\n```")
    
    dependency_section = "\n\n".join(dependency_info) if dependency_info else "No dependency files found"
    
    # Create a prompt for Gemini
    prompt = f"""
    You are a professional technical writer tasked with creating a comprehensive, well-structured README.md file for a GitHub repository.
    
    Repository Information:
    - Name: {repo_name}
    - Description: {repo_description}
    - Primary languages: {', '.join(language_list)}
    - Topics: {', '.join(topics)}
    - Created: {created_at}
    - Last update: {updated_at}
    
    Recent commit messages:
    {chr(10).join(commit_messages)}
    
    Tech Stack:
    {tech_stack_text}
    
    Dependencies and Package Information:
    {dependency_section}
    
    Based on this information, create a professional README.md file that includes:
    1. A clear title and concise description of the project
    2. A comprehensive Tech Stack section that lists all the frameworks, libraries and tools used in the project, organized by category when possible
    3. Installation instructions based on the languages and frameworks used
    4. Dependency information highlighting key frameworks and libraries
    5. Usage examples (use reasonable assumptions)
    6. A features section based on commit messages, topics, and identified frameworks
    7. Contribution guidelines
    8. License information (use {license_name} if specified)
    9. A well-organized structure with proper Markdown formatting
    
    The README should be comprehensive yet concise, use proper Markdown formatting including headers, code blocks, and possibly tables or lists where appropriate. Make reasonable assumptions where information is not provided.
    
    Format the output as clean Markdown suitable for a README.md file, no explanations needed outside the actual README content.
    """

    with st.spinner("Generating README with AI..."):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            st.error(f"Error generating README: {e}")
            return None

# Process button
if st.button("Generate README"):
    if not gemini_api_key:
        st.error("Please enter your Gemini API key in the sidebar")
    elif not repo_url:
        st.error("Please enter a GitHub repository URL")
    else:
        try:
            # Initialize Gemini model
            model = initialize_gemini(gemini_api_key)
            if not model:
                st.error("Failed to initialize Gemini model. Check your API key.")
                st.stop()
            
            # Extract repository information
            username, repo_name = extract_repo_info(repo_url)
            st.info(f"Analyzing repository: {username}/{repo_name}")
            
            # Fetch repo data with progress indicators
            repo_data = fetch_repo_data(username, repo_name, github_token)
            
            if repo_data:
                # Generate README
                readme_content = generate_readme(model, repo_data)
                
                if readme_content:
                    # Display the generated README
                    st.subheader("Generated README")
                    st.markdown(readme_content)
                    
                    # Download button
                    st.download_button(
                        label="Download README.md",
                        data=readme_content,
                        file_name="README.md",
                        mime="text/markdown",
                    )
                    
                    # Copy to clipboard button
                    st.code(readme_content, language="markdown")
                    
                    # Display summary of what was found
                    with st.expander("Repository Analysis Summary"):
                        st.write("### Languages")
                        languages = repo_data.get("languages", {})
                        if languages:
                            # Convert to percentages
                            total = sum(languages.values())
                            language_percentages = {lang: round(bytes/total*100, 1) for lang, bytes in languages.items()}
                            
                            # Display as a horizontal bar chart
                            st.bar_chart(language_percentages)
                        else:
                            st.write("No language information found")
                        
                        st.write("### Detected Technologies")
                        tech_stack = repo_data.get("tech_stack", {})
                        if tech_stack:
                            for category, items in tech_stack.items():
                                st.write(f"**{category}**")
                                for name, version in items:
                                    st.write(f"- {name} ({version})")
                        else:
                            frameworks = repo_data.get("frameworks", [])
                            if frameworks:
                                st.write("- " + "\n- ".join(frameworks))
                            else:
                                st.write("No technologies detected")
        
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.exception(e)

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and Google Gemini")