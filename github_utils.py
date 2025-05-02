import requests
import base64
import json 
from urllib.parse import urlparse
import streamlit as st 


from dependency_parser import identify_dependencies 

def extract_repo_info(repo_url):
    """Extract username and repo name from GitHub URL."""
    parsed_url = urlparse(repo_url)
    path_parts = parsed_url.path.strip('/').split('/')
    if len(path_parts) >= 2:
        username = path_parts[0]
        repo_name = path_parts[1]
        return username, repo_name
    else:
        raise ValueError("Invalid GitHub repository URL format. Please use the format https://github.com/username/repository")

def get_file_content(username, repo_name, file_path, github_token=None):
    """Fetch the content of a specific file from the repository."""
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
        elif content_data.get('type') == 'dir':
             st.warning(f"Expected a file at '{file_path}', but found a directory.")
        else:
             st.warning(f"Could not get content for '{file_path}'. Type: {content_data.get('type')}")
    elif response.status_code == 404:
         st.warning(f"File not found: '{file_path}'")
    else:
        st.warning(f"Error fetching '{file_path}': {response.status_code}")

    return None

def find_files_recursively(username, repo_name, path="", target_files=None, github_token=None):
    """Recursively find target files in the repository."""
    if target_files is None:
        target_files = ["package.json"]
    found_files = []
    headers = {}
    if github_token:
        headers['Authorization'] = f'token {github_token}'

    contents_url = f"https://api.github.com/repos/{username}/{repo_name}/contents/{path}"
    response = requests.get(contents_url, headers=headers)

    if response.status_code != 200:
        st.warning(f"Could not access {path} in repository: {response.status_code}") # Avoid excessive warnings
        return found_files

    contents = response.json()

    if not isinstance(contents, list):
        return found_files

    for item in contents:
        if item['type'] == 'file':
            for target in target_files:
               
                if item['name'] == target or item['path'].endswith(f"/{target}"):
                    if item['path'] not in [f['path'] for f in found_files]:
                         found_files.append({'name': item['name'], 'path': item['path']})
        elif item['type'] == 'dir':
            
            if any(skip in item['path'].lower().split('/') for skip in ['node_modules', 'vendor', 'dist', 'build', '.git', '.github', 'docs', 'tests', 'examples']):
                continue
            
            found_files.extend(find_files_recursively(
                username, repo_name, item['path'], target_files, github_token
            ))

    return found_files


def fetch_repo_data(username, repo_name, github_token=None):
    """Fetch comprehensive repository data from GitHub API."""

    headers = {}
    if github_token:
        headers['Authorization'] = f'token {github_token}'

    progress_bar = st.progress(0)
    progress_text = st.empty()

    repo_data = {} 

    progress_text.text("Fetching repository information...")
    repo_url = f"https://api.github.com/repos/{username}/{repo_name}"
    try:
        repo_response = requests.get(repo_url, headers=headers)
        repo_response.raise_for_status()
        repo_data['repo_info'] = repo_response.json()
        progress_bar.progress(20)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            st.error(f"Repository not found: {username}/{repo_name}. Please check the URL.")
        elif e.response.status_code == 401 or e.response.status_code == 403:
            st.error("Authentication error. Please check your GitHub token or repository privacy settings.")
        else:
            st.error(f"Error fetching repository information: {e}")
        return None 

    progress_text.text("Analyzing languages...")
    langs_url = f"https://api.github.com/repos/{username}/{repo_name}/languages"
    try:
        langs_response = requests.get(langs_url, headers=headers)
        langs_response.raise_for_status()
        repo_data['languages'] = langs_response.json()
        progress_bar.progress(40)
    except requests.exceptions.RequestException as e:
        st.warning(f"Could not fetch language information: {e}")
        repo_data['languages'] = {}

    progress_text.text("Fetching recent commits...")
    commits_url = f"https://api.github.com/repos/{username}/{repo_name}/commits?per_page=5"
    try:
        commits_response = requests.get(commits_url, headers=headers)
        commits_response.raise_for_status()
        commits = commits_response.json()
        repo_data['recent_commits'] = commits[:5] if isinstance(commits, list) else []
        progress_bar.progress(60)
    except requests.exceptions.RequestException as e:
        st.warning(f"Could not fetch commits: {e}")
        repo_data['recent_commits'] = []

    progress_text.text("Looking for existing README...")
    try:
        readme_url = f"https://api.github.com/repos/{username}/{repo_name}/readme"
        readme_response = requests.get(readme_url, headers=headers)
        readme_response.raise_for_status()
        readme_data = readme_response.json()
        repo_data['existing_readme'] = base64.b64decode(readme_data.get('content', '')).decode('utf-8')
    except requests.exceptions.RequestException:
        repo_data['existing_readme'] = "No README found"
    progress_bar.progress(70)

    progress_text.text("Identifying frameworks and dependencies...")
    languages = repo_data.get('languages', {})
    detected_languages = list(languages.keys())

    dependency_file_names_to_search = []
    if 'Python' in detected_languages:
        dependency_file_names_to_search.extend(['requirements.txt', 'Pipfile', 'setup.py', 'pyproject.toml'])
    if 'JavaScript' in detected_languages or 'TypeScript' in detected_languages:
         dependency_file_names_to_search.append('package.json') 
    if 'Ruby' in detected_languages:
        dependency_file_names_to_search.append('Gemfile')
    if 'PHP' in detected_languages:
        dependency_file_names_to_search.append('composer.json')
    if 'Java' in detected_languages:
        dependency_file_names_to_search.extend(['pom.xml', 'build.gradle'])
    if 'Go' in detected_languages:
        dependency_file_names_to_search.append('go.mod')
    if 'Rust' in detected_languages:
        dependency_file_names_to_search.append('Cargo.toml')
    if 'C#' in detected_languages:
         
         pass #


    # Find the paths of these specific files recursively
    found_dep_files = []
    if dependency_file_names_to_search:
         with st.spinner(f"Searching for {', '.join(dependency_file_names_to_search)} files..."):
             found_dep_files = find_files_recursively(
                 username, repo_name,
                 target_files=dependency_file_names_to_search,
                 github_token=github_token
             )

    # Fetch content for found dependency files
    dependency_contents = {}
    if found_dep_files:
        st.info(f"Found {len(found_dep_files)} potential dependency files. Fetching contents...")
        for file_info in found_dep_files:
            content = get_file_content(username, repo_name, file_info['path'], github_token)
            if content:
                dependency_contents[file_info['path']] = content



    dependency_analysis = identify_dependencies(
        dependency_contents, # Pass the file contents
        detected_languages, # Pass the detected languages
        username, repo_name, github_token # Needed for special file checks if kept in identify_dependencies
    )


    repo_data['frameworks'] = dependency_analysis.get('frameworks', [])
    repo_data['dependencies'] = dependency_analysis.get('dependencies', {}) # This is the parsed data, not raw content
    repo_data['tech_stack'] = dependency_analysis.get('tech_stack', {})


    progress_bar.progress(100)
    progress_text.empty()
    st.success("Repository analysis complete!")

    return repo_data

