#!/bin/bash

# Git setup and push script
echo "Setting up Git and pushing to GitHub..."

# You need to replace these with your actual details
read -p "Enter your name: " git_name
read -p "Enter your email: " git_email

# Configure git
git config user.name "$git_name"
git config user.email "$git_email"

# Commit all staged files
git commit -m "Initial commit: Django Box Selection System with comprehensive tests and documentation"

# Add remote repository
git remote add origin https://github.com/SeshasaiTunuguntla/django-box-selection.git

# Push to GitHub
git push -u origin main

echo "Done! Check your repository at: https://github.com/SeshasaiTunuguntla/django-box-selection"
