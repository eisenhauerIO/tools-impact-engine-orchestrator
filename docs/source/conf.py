"""Sphinx configuration for Impact Engine Orchestrator documentation."""

import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

project = "Impact Engine Orchestrator"
author = "eisenhauerIO"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.mathjax",
    "sphinx.ext.extlinks",
    "myst_parser",
    "nbsphinx",
]

# External links shortcuts
extlinks = {
    "repo": ("https://github.com/eisenhauerIO/tools-impact-engine-orchestrator/%s", "%s"),
}

# Show TODO items locally, hide in production builds
todo_include_todos = os.environ.get("SPHINX_PROD", "0") != "1"

# Accept Markdown files as source as well as reStructuredText
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
templates_path = ["_templates"]
exclude_patterns = ["build", "GUIDELINES.md"]
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "navigation_depth": 2,
}
html_static_path = ["_static"]

# Footer with license information
copyright = "eisenhauerIO — MIT License (code) | CC BY 4.0 (content)"

# Enable "Edit on GitHub" link in RTD theme
html_context = {
    "display_github": True,
    "github_user": "eisenhauerIO",
    "github_repo": "tools-impact-engine-orchestrator",
    "github_version": "main",
    "conf_py_path": "/docs/source/",
}

html_extra_path = []

# nbsphinx settings: execute notebooks during build
nbsphinx_execute = "always"
nbsphinx_allow_errors = False

# Add notebook info bar (applies to all notebooks)
_gh_repo = "https://github.com/eisenhauerIO/tools-impact-engine-orchestrator"
_colab = "https://colab.research.google.com/github/eisenhauerIO/tools-impact-engine-orchestrator"
nbsphinx_prolog = rf"""
{{% set docname = env.doc2path(env.docname, base=None) %}}

.. |colab| image:: https://colab.research.google.com/assets/colab-badge.svg
    :target: {_colab}/blob/main/docs/source/{{{{ docname }}}}

.. only:: html

    .. nbinfo::
        Download the notebook `here <{_gh_repo}/blob/main/docs/source/{{{{ docname }}}}>`__!
        Interactive online version: |colab|

"""


def setup(app):
    """Register custom static files with Sphinx."""
    app.add_css_file("custom.css")
