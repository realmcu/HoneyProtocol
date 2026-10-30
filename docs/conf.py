from datetime import datetime
from pathlib import Path


project = "HoneyProtocol"
author = "Realtek Semiconductor"
copyright = f"{datetime.now().year}, Realtek Semiconductor"

extensions = [
    "sphinx.ext.githubpages",
    "sphinx_copybutton",
    "sphinxcontrib.mermaid",
]

source_suffix = {".rst": "restructuredtext"}
master_doc = "index"
language = "zh_CN"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "collapse_navigation": False,
    "navigation_depth": 4,
    "prev_next_buttons_location": "both",
    "style_external_links": True,
    "style_nav_header_background": "#1f4e78",
}
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_show_sourcelink = False
html_show_sphinx = False
html_last_updated_fmt = "%Y-%m-%d"

numfig = True
numfig_secnum_depth = 2
numfig_format = {"table": "表 %s"}

html_context = {
    "display_github": True,
    "github_user": "realmcu",
    "github_repo": "HoneyProtocol",
    "github_version": "main",
    "conf_py_path": "/docs/",
}

mermaid_version = "11.17.2"
copybutton_prompt_text = r"^\$ |^> |^python tools/"
copybutton_prompt_is_regexp = True
