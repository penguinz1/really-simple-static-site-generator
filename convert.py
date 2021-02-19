from distutils.dir_util import copy_tree
import os
import re
import pymmd
import warnings
import sys

INPUT_ROOT = "input"
OUTPUT_ROOT = "penguinz1.github.io"

if (len(sys.argv) == 2):
    OUTPUT_ROOT = sys.argv[1]

if (len(sys.argv) >= 3):
    INPUT_ROOT = sys.argv[1]
    OUTPUT_ROOT = sys.argv[2]

# copy static files to output directory
copy_tree(f'{INPUT_ROOT}/static', f'{OUTPUT_ROOT}/static')

# get all files in input directory
files = os.listdir(INPUT_ROOT)

# convert included files
def convertInclude(location):
    # clean location
    location = location.replace("'", "")
    location = location.replace('"', "")
    try:
        if (location.endswith(".html")): # convert html file
            file = open(location, 'r')
            content = file.read()
            return content
        elif (location.endswith(".md")): # convert markdown file, extracting the body portion
            file = open(location, 'r')
            raw_content = file.read()
            html_content = pymmd.convert(raw_content)
            content = re.search("<body>([\s\S]*)</body>", html_content)
            if (content):
                return content.group(1)
            else:
                return ""
        else: # file is not recognized as an appropriate format
            warnings.warn(f'{location} is not recognized as a .html or .md file. Ignoring.', RuntimeWarning)
            return ""
    except FileNotFoundError:
        warnings.warn(f'{location} was not found. Ignoring.', RuntimeWarning)
        return ""

# convert HTML snippets
def convertHTMLSnippet(snippet):
    content = snippet.split("\n")
    output = ""
    for line in content:
        # check for include syntax
        if (re.search("{% include (.+) %}", line)):
            addon = re.search("{% include (.+) %}", line).group(1)
            to_include = convertInclude(f'{INPUT_ROOT}/{addon}')
            output += to_include
        else:
            output += line
    return output

# convert HTML files
def convertHTML(location):
    # open file and read line
    file = open(location, 'r')
    line = file.readline()

    # get template
    template = re.search("{% [e]xtends (.+) %}", line)

    # output page
    page = ""

    # case for no template
    if (not template):
        while (line):
            # check for include syntax
            if (re.search("{% include (.+) %}", line)):
                addon = re.search("{% include (.+) %}", line).group(1)
                to_include = convertInclude(f'{INPUT_ROOT}/{addon}')
                page += to_include
            else: # add line
                page += line
            line = file.readline()
        return page

    # case for template
    try:
        template_name = template.group(1)
        # clean template name
        template_name = template_name.replace("'", "")
        template_name = template_name.replace('"', "")
        if (not template_name.endswith(".html")):
            raise RuntimeError(f'{template_name} must be a .html file. Conversion Aborted.')
        template_file = open(f'{INPUT_ROOT}/{template_name}', 'r')
    except FileNotFoundError:
        raise RuntimeError(f'The file "{template_name}" was not found. Conversion Aborted.')

    old_lines = line + file.read()
    line = template_file.readline()
    while (line):
        if (re.search("{% endblock %}", line)): # ignore endblock tags
            line = template_file.readline()
            continue

        if (re.search("{% include (.+) %}", line)): # check for include syntax
            addon = re.search("{% include (.+) %}", line).group(1)
            to_include = convertInclude(f'{INPUT_ROOT}/{addon}')
            page += to_include
        elif (re.search("{% block (.+) %}", line)): # check for block syntax
            block = re.search("{% block (.+) %}", line).group(1)
            match = re.search("{% block " + block + " %}([\s\S]*?){% endblock %}", old_lines)
            if (match):
                page += convertHTMLSnippet(match.group(1))
                while (not re.search("{% endblock %}", line)):
                    line = template_file.readline()
                    if (not line):
                        raise RuntimeError("{% endblock %} tag not found!")
        else: # add line
            page += line
        line = template_file.readline()
    return page

def convertMarkdown(location):
    # open file and read content
    file = open(location, 'r')
    content = file.read()

    # return converted markdown
    return pymmd.convert(content)

# start converting all files
for file in files:
    # ignore marked files
    if (re.search("_ignore", file)):
        continue

    # process .html files
    if (file.endswith(".html")):
        page = convertHTML(f'{INPUT_ROOT}/{file}')
        with open(f'{OUTPUT_ROOT}/{file}', "w") as output:
            output.write(page)

    # process .md files
    elif (file.endswith(".md")):
        page = convertMarkdown(f'{INPUT_ROOT}/{file}')
        # replace .md with .html
        with open(f'{OUTPUT_ROOT}/{file[0:-3]}.html', "w") as output:
            output.write(page)