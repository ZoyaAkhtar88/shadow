#!/bin/bash

# Configurations
BITBUCKET_USER="7171618-admin"
APP_PASSWORD="noobhubhai87"  # Store securely, not in plain text
WORKSPACE="7171618"
REPO_SLUG="git clone https://7171618-admin@bitbucket.org/7171618/shadwo.git"
BRANCH="main"

# Wait 2 minutes before retrying
sleep 120

# Trigger pipeline restart
curl -X POST -u "$BITBUCKET_USER:$APP_PASSWORD" \
  "https://api.bitbucket.org/2.0/repositories/$WORKSPACE/$REPO_SLUG/pipelines/" \
  -H "Content-Type: application/json" \
  -d "{\"target\": {\"ref_type\": \"branch\", \"type\": \"pipeline_ref_target\", \"ref_name\": \"$BRANCH\"}}"