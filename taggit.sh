#!/bin/zsh

# Check if tag name and message are provided
if [[ -z "$1" || -z "$2" ]]; then
  echo "Usage: $0 <tag-name> <tag-message>"
  exit 1
fi

# Create an annotated tag
git tag -a "$1" -m "$2"

# Check if tag creation was successful
if [[ $? -ne 0 ]]; then
  echo "Error: Failed to create tag."
  exit 1
fi

# Push the tag
git push origin "$1"

# Check if push was successful
if [[ $? -ne 0 ]]; then
  echo "Error: Failed to push tag."
  exit 1
fi

echo "Tag '$1' created and pushed successfully."

git tag -n