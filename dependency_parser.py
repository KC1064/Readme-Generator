import json
import streamlit as st 


def parse_package_json(content):
    """Parse package.json content to extract dependencies and dev dependencies."""
    try:
        data = json.loads(content)
        dependencies = data.get('dependencies', {})
        dev_dependencies = data.get('devDependencies', {})
        return dependencies, dev_dependencies
    except json.JSONDecodeError:
        st.warning(f"Could not parse package.json content.")
        return {}, {}
    except AttributeError:
        st.warning(f"Invalid content passed to parse_package_json.")
        return {}, {}


def extract_tech_stack_from_packages(dependencies, dev_dependencies):
    """Extract tech stack information from JS/TS dependencies dictionaries (package.json)."""
    
    frontend_frameworks = {
        'react': 'React', 'vue': 'Vue.js', 'angular': 'Angular', 'svelte': 'Svelte',
        'next': 'Next.js', 'nuxt': 'Nuxt.js', 'gatsby': 'Gatsby',
    }
    backend_frameworks = {
        'express': 'Express.js', 'koa': 'Koa.js', 'fastify': 'Fastify', 'nest': 'NestJS',
        'apollo-server': 'Apollo Server', 'graphql': 'GraphQL', # Can be frontend/backend, listed here for detection
    }
    ui_libraries = {
        'material-ui': 'Material-UI', '@mui/material': 'Material-UI', 'antd': 'Ant Design',
        'bootstrap': 'Bootstrap', 'tailwindcss': 'Tailwind CSS', '@chakra-ui/react': 'Chakra UI',
        '@emotion': 'Emotion', 'styled-components': 'Styled Components',
    }
    state_management = {
        'redux': 'Redux', 'mobx': 'MobX', 'recoil': 'Recoil', 'zustand': 'Zustand',
        '@reduxjs/toolkit': 'Redux Toolkit',
    }
    testing_frameworks = {
        'jest': 'Jest', 'mocha': 'Mocha', 'cypress': 'Cypress', '@testing-library': 'Testing Library',
        'vitest': 'Vitest', 'playwright': 'Playwright',
    }
    build_tools = {
        'webpack': 'Webpack', 'vite': 'Vite', 'rollup': 'Rollup', 'parcel': 'Parcel',
        'esbuild': 'esbuild', 'babel': 'Babel', '@babel/core': 'Babel', 'typescript': 'TypeScript',
        'gulp': 'Gulp', 'grunt': 'Grunt',
    }
    other_tech = {
        'prettier': 'Prettier', 'eslint': 'ESLint', 'nodemon': 'Nodemon', ' concurrently': 'Concurrently', # space to avoid matching 'concurrently' within other words
    }


    all_deps = {**dependencies, **dev_dependencies}
    identified_technologies = {} 

    for dep, version in all_deps.items():
        dep_lower = dep.lower()

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
                    if category not in identified_technologies:
                        identified_technologies[category] = {}
                    identified_technologies[category][name] = version # Use name as key to handle duplicates
                    break 
                
    formatted_tech_stack = []
    for category, items in identified_technologies.items():
         for name, version in items.items():
              formatted_tech_stack.append((category, name, version))
    return formatted_tech_stack


def parse_requirements_txt(content):
    """Parse requirements.txt content to extract dependencies."""
    dependencies = {}
    if not isinstance(content, str):
        return {}
    lines = content.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        parts = line.split(';', 1) 
        package_spec = parts[0].strip()

        if '==' in package_spec:
            name, version = package_spec.split('==', 1)
            dependencies[name.strip()] = version.strip()
        elif '>=' in package_spec:
             name, version = package_spec.split('>=', 1)
             dependencies[name.strip()] = f">={version.strip()}"
        elif '<=' in package_spec:
             name, version = package_spec.split('<=', 1)
             dependencies[name.strip()] = f"<={version.strip()}"
        elif '>' in package_spec:
             name, version = package_spec.split('>', 1)
             dependencies[name.strip()] = f">{version.strip()}"
        elif '<' in package_spec:
             name, version = package_spec.split('<', 1)
             dependencies[name.strip()] = f"<{version.strip()}"
        elif '~=' in package_spec:
             name, version = package_spec.split('~=', 1)
             dependencies[name.strip()] = f"~={version.strip()}"
        else:
            name = package_spec
            if '[' in name and ']' in name:
                 name = name.split('[', 1)[0].strip()
            if name:
                dependencies[name] = "Any" 

    return dependencies


def identify_dependencies(raw_dependency_contents, languages):
    """
    Identifies frameworks and dependencies by parsing provided raw contents
    of package.json and requirements.txt files only.
    """
    parsed_dependencies = {} 
    frameworks = [] 
    tech_stack_info = {} 

    
    for file_path, content in raw_dependency_contents.items():
        file_name_lower = file_path.lower().split('/')[-1] 

        if file_name_lower == 'package.json':
            main_deps, dev_deps = parse_package_json(content)
            parsed_dependencies[file_path] = {'dependencies': main_deps, 'devDependencies': dev_deps}

            stack_info_list = extract_tech_stack_from_packages(main_deps, dev_deps)

        
            for category, name, version in stack_info_list:
                if category not in tech_stack_info:
                    tech_stack_info[category] = []
                \
                item = (name, version)
                if item not in tech_stack_info[category]:
                    tech_stack_info[category].append(item)

                if name not in frameworks:
                    frameworks.append(name)

        elif file_name_lower == 'requirements.txt':
            req_deps = parse_requirements_txt(content)
            # Store parsed deps by file path
            parsed_dependencies[file_path] = {'dependencies': req_deps}

            # Add Python dependencies to frameworks list and a 'Python Dependencies' category in tech_stack
            if req_deps:
                 # Add category to tech_stack
                 python_deps_category = 'Python Dependencies'
                 if python_deps_category not in tech_stack_info:
                      tech_stack_info[python_deps_category] = []

                 # Add dependencies to tech_stack category and frameworks list
                 for name, version in req_deps.items():
                      item = (name, version)
                      # Avoid adding duplicate (name, version) pairs within the category
                      if item not in tech_stack_info[python_deps_category]:
                           tech_stack_info[python_deps_category].append(item)
                      # Add to main frameworks list
                      if name not in frameworks:
                           frameworks.append(name)

        
    frameworks = list(set(frameworks))

    
    cleaned_tech_stack_info = {}
    for category, items in tech_stack_info.items():
        cleaned_tech_stack_info[category] = []
        seen_items = set() #
        for name, version in items:
            item = (name, version)
            if item not in seen_items:
                 cleaned_tech_stack_info[category].append(item)
                 seen_items.add(item)

    return {
        'parsed_dependencies': parsed_dependencies, 
        'frameworks': frameworks, 
        'tech_stack': cleaned_tech_stack_info 
    }