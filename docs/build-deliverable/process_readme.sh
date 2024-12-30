#!/bin/bash

# Steps used to integrate the README directly into the built PDF.
# Superseded by 00_introduction.md file.

# Process README
# --------------

# Copy README here for edits
cp ../../README.md .
mv README.md 00_README.md

# pdflatex cannot include SVGs. Some SVGs get included also as the github badges.
sed -i '' 's/smashcima-logo.svg/smashcima-logo.png/' 00_README.md
sed -i '' '/^.*.svg.*$/d' 00_README.md
sed -i '' '/^\[\!/d' 00_README.md
sed -i '' '/^\!\[/d' 00_README.md
# Note: the -i '' is here because on mac, sed -i expects an extension argument.
# See: https://stackoverflow.com/questions/19456518/error-when-using-sed-with-find-command-on-os-x-invalid-command-code/79153150#79153150

# pdflatex cannot include the Huggingface emoji.
sed -i '' 's/on \[.* Huggingface/on \[Huggingface/' 00_README.md

# Title image with logo not rendered in div
sed -i '' '/^<[\/]?div/d' 00_README.md

# Indented tags rendered as code
sed -i '' 's/^    <br/<br/' 00_README.md

# PMCG logo from assets
sed -i '' 's/https:\/\/ufal.mff.cuni.cz\/\~hajicj\/2024\/images/assets/' 00_README.md

# Add chapter title
sed -i '' '1s/^/# Introduction/' 00_README.md

# Build README
# ------------
#pandoc 00_README.md -o 00_README.html -s --resource-path=..\;../assets --extract-media=media/ --metadata title="Smashcima Technical Documentation"
#pandoc 00_README.html -o 00_README.pdf


