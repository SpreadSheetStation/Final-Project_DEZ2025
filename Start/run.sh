#!/bin/bash

# run.sh
# Sets environment variables and creates terraform.tfvars for Final-Project_DEZ2025.
# Run with: source ./run.sh
# Instructions: Edit GCS_BUCKET_NAME, GCP_PROJECT_ID, BQ_DATASET_NAME below.
# Ensure one .json file in gcp_key/ and kaggle_key/.

# Check if sourced
if [ "$0" = "$BASH_SOURCE" ]; then
  echo "Error: Use 'source ./run.sh' to set environment variables."
  exit 1
fi

# Get script directory reliably
SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(dirname "$(realpath "$SCRIPT_PATH")")"

# Error handler (avoids closing terminal)
error() {
  echo "$1" >&2
  return 1
}

# Set GCP credentials path
GCP_JSON=$(ls "$SCRIPT_DIR/gcp_key/"*.json 2>/dev/null)
[ -z "$GCP_JSON" ] && error "Error: No .json file in $SCRIPT_DIR/gcp_key/" && return
[ $(ls "$SCRIPT_DIR/gcp_key/"*.json | wc -l) -gt 1 ] && error "Error: Multiple .json files in $SCRIPT_DIR/gcp_key/" && return
export GCP_CREDENTIALS_PATH="$GCP_JSON"

# Set Kaggle credentials path
KAGGLE_JSON=$(ls "$SCRIPT_DIR/kaggle_key/"*.json 2>/dev/null)
[ -z "$KAGGLE_JSON" ] && error "Error: No .json file in $SCRIPT_DIR/kaggle_key/" && return
[ $(ls "$SCRIPT_DIR/kaggle_key/"*.json | wc -l) -gt 1 ] && error "Error: Multiple .json files in $SCRIPT_DIR/kaggle_key/" && return
export KAGGLE_CREDENTIALS_PATH="$KAGGLE_JSON"

# User-editable variables
export GCS_BUCKET_NAME="zomaarietsblabla2025xyz"
export GCP_PROJECT_ID="cryptopipeline-456916"
export BQ_DATASET_NAME="bqBitcoin"

# Show variables
echo "Environment variables set:"
echo "GCP_CREDENTIALS_PATH=$GCP_CREDENTIALS_PATH"
echo "KAGGLE_CREDENTIALS_PATH=$KAGGLE_CREDENTIALS_PATH"
echo "GCS_BUCKET_NAME=$GCS_BUCKET_NAME"
echo "GCP_PROJECT_ID=$GCP_PROJECT_ID"
echo "BQ_DATASET_NAME=$BQ_DATASET_NAME"

# Create terraform.tfvars
TERRAFORM_DIR="$SCRIPT_DIR/../terraform"
TERRAFORM_FILE="$TERRAFORM_DIR/terraform.tfvars"

[ ! -d "$TERRAFORM_DIR" ] && error "Error: $TERRAFORM_DIR does not exist" && return
[ -f "$TERRAFORM_FILE" ] && [ ! -w "$TERRAFORM_FILE" ] && error "Error: $TERRAFORM_FILE is not writable" && return

cat > "$TERRAFORM_FILE" << EOL
# Path to your GCP service account key JSON file
credentials = "$GCP_CREDENTIALS_PATH"

# Your GCP project ID
project = "$GCP_PROJECT_ID"

# Globally unique GCS bucket name
gcs_bucket_name = "$GCS_BUCKET_NAME"

# BigQuery dataset name
bq_dataset_name = "$BQ_DATASET_NAME"

# No need to change this
region = "us-central"
location = "US"
EOL

[ -f "$TERRAFORM_FILE" ] && echo "Updated $TERRAFORM_FILE:" && cat "$TERRAFORM_FILE" || error "Error: Failed to create $TERRAFORM_FILE" && return

echo "Note: Edit GCS_BUCKET_NAME, GCP_PROJECT_ID, BQ_DATASET_NAME in this script if needed."