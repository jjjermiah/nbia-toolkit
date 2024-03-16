# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import html
import os
import sys

sys.path.insert(0, os.path.abspath("../src"))
# -- Project information -----------------------------------------------------

project = "nbiatoolkit"
copyright = "2023, Jermiah Joseph"
author = "Jermiah Joseph"

import nbiatoolkit

# The full version, including alpha/beta/rc tags
release: str = nbiatoolkit.__version__

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "myst_nb",
    "autoapi.extension",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_tabs.tabs",
    "sphinx_exec_code",
    "sphinx.ext.autosectionlabel",
]
autoapi_dirs = ["../src/nbiatoolkit"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "_html_notebooks"]


exec_code_working_dir = ".."
exec_code_source_folders = ["../src"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = "piccolo_theme"
html_theme = "sphinx_rtd_theme"

# # user starts in dark mode
# default_dark_mode = True

html_static_path = ["_static"]

# html_css_files = [
#     "css/custom.css",
# ]
# def setup(app):
#     app.add_css_file("css/custom.css")
