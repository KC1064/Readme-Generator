import json
import streamlit as st # For warnings/info messages

# Potentially import github_utils if you need to fetch files *from here*,
# but in the revised plan, github_utils.fetch_repo_data fetches and passes content.
# We might still need it for the special file check. Let's keep the special file
# check logic here and adapt it.

# Import github_utils functions if needed for special file check or finding (less ideal, circular)
# from github_utils import get_file_content # If identify_dependencies still fetches some files

def parse_package_json(content):
    """Parse package.json content to extract dependencies and dev dependencies."""
    try:
        data = json.loads(content)
        dependencies = data.get('dependencies', {})
        dev_dependencies = data.get('devDependencies', {})
        return dependencies, dev_dependencies
    except json.JSONDecodeError:
        st.warning("Could not parse package.json content")
        return {}, {}
    except AttributeError:
        st.warning("Invalid content passed to parse_package_json")
        return {}, {}


def extract_tech_stack_from_packages(dependencies, dev_dependencies):
    """Extract tech stack information from dependencies dictionaries."""
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

    # Common backend frameworks (JS/TS specific)
    backend_frameworks = {
        'express': 'Express.js',
        'koa': 'Koa.js',
        'fastify': 'Fastify',
        'nest': 'NestJS',
        'apollo-server': 'Apollo Server',
        'graphql': 'GraphQL', # Can be frontend/backend, list here for detection
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
        '@testing-library': 'Testing Library', # covers @testing-library/react etc.
        'vitest': 'Vitest',
        'playwright': 'Playwright',
    }

    # Build tools / Compilers
    build_tools = {
        'webpack': 'Webpack',
        'vite': 'Vite',
        'rollup': 'Rollup',
        'parcel': 'Parcel',
        'esbuild': 'esbuild',
        'babel': 'Babel',
        '@babel/core': 'Babel',
        'typescript': 'TypeScript',
        'gulp': 'Gulp',
        'grunt': 'Grunt',
    }

    # Other common technologies detectable via package.json
    other_tech = {
        'prettier': 'Prettier',
        'eslint': 'ESLint',
        'nodemon': 'Nodemon',
        ' concurrently': 'Concurrently', # space to avoid matching 'concurrently' within other words
    }


    # Check all dependencies
    all_deps = {**dependencies, **dev_dependencies}
    identified_technologies = {} # Use a dict to avoid duplicates and store category

    for dep, version in all_deps.items():
        dep_lower = dep.lower()

        # Check against all categories
        for category, lookup in [
            ('Frontend', frontend_frameworks),
            ('Backend', backend_frameworks),
            ('UI', ui_libraries),
            ('State Management', state_management),
            ('Testing', testing_frameworks),
            ('Build Tools', build_tools),
            ('Other Tools', other_tech),
        ]:
            for key, name in lookup.items():
                if key.lower() in dep_lower:
                    # Store as (name, version) under the category, prevent duplicates
                    if category not in identified_technologies:
                        identified_technologies[category] = {}
                    identified_technologies[category][name] = version # Use name as key to handle duplicates
                    break # Move to the next dependency once a match is found


    # Convert the nested dict to the desired list format
    formatted_tech_stack = []
    for category, items in identified_technologies.items():
         for name, version in items.items():
              formatted_tech_stack.append((category, name, version))


    return formatted_tech_stack


# Modified identify_dependencies to accept file contents and languages
def identify_dependencies(dependency_contents, languages, username, repo_name, github_token=None):
    """
    Identifies frameworks and dependencies based on provided file contents
    and detected languages.
    """
    parsed_dependencies = {}
    frameworks = []
    tech_stack_info = {} # Use a dict to aggregate tech stack by category

    # Process package.json files if found
    for file_path, content in dependency_contents.items():
        if file_path.lower().endswith('package.json'):
            main_deps, dev_deps = parse_package_json(content)
            # Store parsed deps by file path if needed later, or aggregate
            parsed_dependencies[file_path] = {'dependencies': main_deps, 'devDependencies': dev_deps}

            # Extract tech stack from this package.json
            stack_info_list = extract_tech_stack_from_packages(main_deps, dev_deps)

            # Aggregate into tech_stack_info dictionary
            for category, name, version in stack_info_list:
                if category not in tech_stack_info:
                    tech_stack_info[category] = []
                # Avoid adding duplicate (name, version) pairs within a category
                if (name, version) not in tech_stack_info[category]:
                    tech_stack_info[category].append((name, version))

                # Add to frameworks list if not already there
                if name not in frameworks:
                    frameworks.append(name)

    

    special_framework_files_in_root = {
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
        'pom.xml': 'Maven',
        'build.gradle': 'Gradle',
        'Gemfile': 'Ruby on Rails' if 'Gemfile.lock' in dependency_contents else 'Ruby', # Simple guess
        'composer.json': 'Composer', # PHP
        'requirements.txt': 'Python Libraries',
    }

    fetched_paths = dependency_contents.keys()

    for file_path in fetched_paths:
        file_name = file_path.split('/')[-1] # Get base name
        if file_name in special_framework_files_in_root:
             framework_name = special_framework_files_in_root[file_name]
             if framework_name not in frameworks:
                  frameworks.append(framework_name)
        if file_name.endswith('.vue') and 'Vue.js' not in frameworks:
             frameworks.append('Vue.js')
       


    
    final_tech_stack_list = []
    for category, items in tech_stack_info.items():
        final_tech_stack_list.append((category, items)) 

    return {
        'parsed_dependencies': parsed_dependencies, 
        'frameworks': list(set(frameworks)), 
        'tech_stack': tech_stack_info 
    }

