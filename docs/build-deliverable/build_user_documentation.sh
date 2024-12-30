#!/usr/bin/env bash
# Build script for Smashcima docs in PDF format.
# Run from this directory (/docs/build)!

DOCNAME=smashcima-user-documentation


# Preparation
# -----------

# Make sure images are properly linked for the HTML intermediate step
if [ ! -L assets ]; then
    ln -s ../assets/ assets
fi
if [ ! -L docs ]; then
    ln -s ../ docs
fi


# Cleanup
# -------

_SUFFIXES="aux log tex toc"
for SUFFIX in `echo $_SUFFIXES`; do
  if [ -f ${DOCNAME}.${SUFFIX} ]; then rm ${DOCNAME}.${SUFFIX}; fi
done

# Process README
# --------------
# ...this is superspeded by custom 00_introduction.md above. 
# The script with steps that were done here is in process_readme.sh


# HTML build
# ----------

# This is a separate step because in html, including images works properly.
pandoc -s --resource-path=..\;../assets --extract-media=media/ --metadata title="Smashcima User Documentation" ../00_introduction.md ../tutorials/*.md -o ${DOCNAME}.html


# PDF build
# ---------

# First we build tex, to inspect errors.
pandoc ${DOCNAME}.html -o ${DOCNAME}.tex -s --toc --top-level-division chapter -V geometry:margin=2.5cm --metadata-file=defaults.yaml --number-sections
 # --template pandoc_smashcima_template.latex

# Then convert to PDF (do this twice to get hyperref and TOC correctly)
pdflatex ${DOCNAME}.tex
pdflatex ${DOCNAME}.tex
