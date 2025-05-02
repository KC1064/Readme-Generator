# github_utils.py

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
                # GitHub API returns content in base64
                decoded_content = base64.b64decode(content_data['content']).decode('utf-8')
                return decoded_content
            except Exception as e:
                st.warning(f"Error decoding content of {file_path}: {e}")
        # Handle cases where the path is a directory but API returns 200 for info
        elif content_data.get('type') == 'dir':
             st.warning(f"Expected a file at '{file_path}', but found a directory.")
        else:
             st.warning(f"Could not get content for '{file_path}'. Type: {content_data.get('type')}")
    elif response.status_code == 404:
         # st.info(f"File not found: '{file_path}'") # Info is less intrusive than warning
         pass # File not found is common, just return None
    else:
        st.warning(f"Error fetching '{file_path}': {response.status_code}")

    return None



def find_files_recursively(username, repo_name, path="", target_files=None, github_token=None, current_depth=0, depth_limit=None):
    """
    Recursively find target files in the repository up to a specified depth.
    depth_limit=0 means only the starting path (root).
    depth_limit=1 means starting path and its immediate subdirectories.
    """
    if target_files is None:
        target_files = [] 
    if depth_limit is not None and current_depth > depth_limit:
        return []

    found_files = []
    headers = {}
    if github_token:
        headers['Authorization'] = f'token {github_token}'

    contents_url = f"https://api.github.com/repos/{username}/{repo_name}/contents/{path}"
    response = requests.get(contents_url, headers=headers)

    if response.status_code != 200:
        return found_files

    contents = response.json()

    if not isinstance(contents, list):
        return found_files

    for item in contents:
        item_name = item.get('name', '')
        item_path = item.get('path', '')

        if item['type'] == 'file':
            if item_name.lower() in [tf.lower() for tf in target_files]:
                 # Ensure we don't add duplicates based on path
                if item_path not in [f['path'] for f in found_files]:
                     found_files.append({'name': item.get('name', item_name), 'path': item.get('path', item_path)})
        elif item['type'] == 'dir':
            skip_dirs = ['node_modules', 'vendor', 'dist', 'build', '.git', '.github', 'docs', 'tests', 'examples']
            path_parts = item_path.lower().split('/')
            if any(skip in path_parts for skip in skip_dirs):
                 continue

            found_files.extend(find_files_recursively(
                username, repo_name, item_path, target_files, github_token,
                current_depth=current_depth + 1, depth_limit=depth_limit # Pass updated depth and limit
            ))

    return found_files


def fetch_repo_data(username, repo_name, github_token=None):
    """Fetch comprehensive repository data with limited file search (package.json, requirements.txt)."""

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
    except requests.exceptions.RequestException as e:
         st.error(f"Network error fetching repository information: {e}")
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
        
        readme_content_encoded = readme_data.get('content', '')
        if readme_content_encoded:
             repo_data['existing_readme'] = base64.b64decode(readme_content_encoded).decode('utf-8')
        else:
             repo_data['existing_readme'] = "No README found or content is empty"
    except requests.exceptions.RequestException:
         
        repo_data['existing_readme'] = "No README found"
    progress_bar.progress(70)


    
    languages = repo_data.get('languages', {})
    detected_languages = list(languages.keys())

    files_to_search = set()

    if 'JavaScript' in detected_languages or 'TypeScript' in detected_languages:
        files_to_search.add('package.json')

    if 'Python' in detected_languages:
         files_to_search.add('requirements.txt')

    progress_text.text(f"Searching up to depth 2 for {', '.join(list(files_to_search))}...")


    found_dep_files = [] 
    raw_dependency_contents = {} 
    processed_paths = set() 

    
    limited_search_depth = 2 

    if files_to_search:
         search_list = list(files_to_search)
         with st.spinner(f"Searching up to depth {limited_search_depth} for {', '.join(search_list)}..."):
              limited_depth_files = find_files_recursively(
                 username, repo_name,
                 path="", 
                 target_files=search_list,
                 github_token=github_token,
                 depth_limit=limited_search_depth 
             )
              for f in limited_depth_files:
                   if f['path'] not in processed_paths:
                       found_dep_files.append(f)
                       processed_paths.add(f['path'])


    
    if found_dep_files:
        st.info(f"Found {len(found_dep_files)} dependency files. Fetching contents...")
        for file_info in found_dep_files:
            
             if file_info['path'] in processed_paths:
                 content = get_file_content(username, repo_name, file_info['path'], github_token)
                 if content is not None: # get_file_content returns None on error/not found
                     raw_dependency_contents[file_info['path']] = content


   
    dependency_analysis = identify_dependencies(
        raw_dependency_contents,
        detected_languages 
    )


    repo_data['raw_dependency_contents'] = raw_dependency_contents # Keep raw for prompt
    repo_data['frameworks'] = dependency_analysis.get('frameworks', []) # Simple list
    repo_data['tech_stack'] = dependency_analysis.get('tech_stack', {}) # Structured dict
    repo_data['parsed_dependencies'] = dependency_analysis.get('parsed_dependencies', {}) # Optional: store full parsed data per file


    progress_bar.progress(100)
    progress_text.empty()
    st.success("Repository analysis complete!")

    return repo_data