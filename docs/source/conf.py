# -*- coding: utf-8 -*-
#
# cdms2 documentation build configuration file, created by
# sphinx-quickstart on Wed Aug 17 14:33:12 2016.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.
from future.standard_library import install_aliases
install_aliases()
import sys
import os

import sys
import os
import shlex
import easydev
import glob

# html_theme_path = [easydev.get_path_sphinx_themes()]

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0,os.path.join(sys.prefix,"lib","python3.7","site-packages"))
sys.path.insert(0,os.path.join(sys.prefix,"lib","python2.7","site-packages"))
print(os.path.join(sys.prefix,"lib","python3.7","site-packages"))
os.environ['UVCDAT_ANONYMOUS_LOG']="False"
import MV2





# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
#extensions = [
#    'easydev.copybutton',
#    'sphinx.ext.viewcode',
#    'sphinx.ext.imgmath',
#    'sphinx.ext.ifconfig',
#    'sphinx.ext.coverage',
#    'sphinx.ext.doctest',
#    'sphinx.ext.intersphinx',
#    'matplotlib.sphinxext.only_directives',
#    'matplotlib.sphinxext.plot_directive',
#    'sphinx.ext.napoleon'
#]
extensions = [
    "sphinx.ext.autodoc",
#    "readthedocs_ext.readthedocs",
    'easydev.copybutton',
    'sphinx.ext.autosummary',
    'sphinx.ext.todo',
    'sphinx.ext.graphviz',
    'sphinx.ext.doctest',
    'sphinx.ext.viewcode',
    "numpydoc"
#    'sphinx.ext.napoleon'
]

jscopybutton_path = "copybutton.js"

try:
    from easydev.copybutton import get_copybutton_path 
    from easydev.copybutton import copy_javascript_into_static_path
    copy_javascript_into_static_path("_static", get_copybutton_path())
except Exception:
    print("could not copy the copybutton javascript")

# napoleon_google_docstring = True
# napoleon_numpy_docstring = True
# napoleon_include_private_with_doc = False
# napoleon_include_special_with_doc = True
# napoleon_use_admonition_for_examples = True
# napoleon_use_admonition_for_notes = True
# napoleon_use_admonition_for_references = True
# napoleon_use_ivar = False
# napoleon_use_rtype = False
# napolean_use_param = False
numpydoc_show_class_members = False

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The encoding of source files.
#source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'CDAT'
copyright = u'2019'
author = u'Charles Doutriaux-1'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '8.1'
# The full version, including alpha/beta/rc tags.
release = '8.1.2'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build', '_templates']

# The reST default role (used for this markup: `text`) to use for all
# documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
#keep_warnings = False

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# themedir = os.path.join(os.pardir, 'scipy-sphinx-theme', '_theme')
# if not os.path.isdir(themedir):
#     raise RuntimeError("Get the scipy-sphinx-theme first, "
#                        "via git submodule init && git submodule update")


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#html_theme = 'alabaster'
#html_theme = 'sphinxdoc'
#html_theme = 'nature'
html_theme = 'agogo'
#html_theme = 'scipy'
#html_theme = 'pyramid'
#html_theme = 'epub'
#html_theme = 'haiku'
#html_theme = "sphinx_rtd_theme"
#html_theme = 'classic'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#html_theme_options = { "stickysidebar" : "true" }
html_theme_options = { "headerbg" : "#01796F" }

# Add any paths that contain custom themes here, relative to this directory.
#html_theme_path = []
#html_theme_path = [themedir]


# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = " UV-CDAT Utilities Manual"

# A shorter title for the navigation bar.  Default is the same as html_title.
#html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = 'manual/images/cdms_logo2_nocube.png'

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
# html_favicon = 'globe.png'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied
# directly to the root of the documentation.
#html_extra_path = []

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
#html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
#html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}

# If false, no module index is generated.
#html_domain_indices = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
#html_split_index = False

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = True 

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
#html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
#html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = None

# Language to be used for generating the HTML full-text search index.
# Sphinx supports the following languages:
#   'da', 'de', 'en', 'es', 'fi', 'fr', 'hu', 'it', 'ja'
#   'nl', 'no', 'pt', 'ro', 'ru', 'sv', 'tr'
#html_search_language = 'en'

# A dictionary with options for the search language support, empty by default.
# Now only 'ja' uses this config value
#html_search_options = {'type': 'default'}

# The name of a javascript file (relative to the configuration directory) that
# implements a search results scorer. If empty, the default will be used.
#html_search_scorer = 'scorer.js'

# Output file base name for HTML help builder.
htmlhelp_basename = 'cdms2doc'

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
# The paper size ('letterpaper' or 'a4paper').
#'papersize': 'letterpaper',

# The font size ('10pt', '11pt' or '12pt').
#'pointsize': '10pt',

# Additional stuff for the LaTeX preamble.
#'preamble': '',

# Latex figure (float) alignment
#'figure_align': 'htbp',
  'classoptions': ',oneside',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
  (master_doc, 'cdms2.tex', u'uv-cdat',
   u'Denis Nadeau', 'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
latex_logo = 'manual/images/cdms_logo2_nocube.png'

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
latex_toplevel_sectioning = "chapter"

# If true, show page references after internal links.
#latex_show_pagerefs = False

# If true, show URL addresses after external links.
#latex_show_urls = False

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_domain_indices = True


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'cdms', u'Community Data Management System',
     [author], 1)
]

# If true, show URL addresses after external links.
#man_show_urls = False


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
  (master_doc, 'cdms2', u'cdms2 Documentation',
   author, 'cdms2', 'One line description of project.',
   'Miscellaneous'),
]

# Documents to append as an appendix to all manuals.
#texinfo_appendices = []

# If false, no module index is generated.
#texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
#texinfo_show_urls = 'footnote'

# If true, do not generate a @detailmenu in the "Top" node's menu.
#texinfo_no_detailmenu = False


# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'https://docs.python.org/': None}


