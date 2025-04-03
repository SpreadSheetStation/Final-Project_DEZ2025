variable "credentials" {
  description = "Path to GCP service account key JSON"
  type        = string
}

variable "project" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "gcs_bucket_name" {
  description = "Name of the GCS bucket"
  type        = string
}

variable "bq_dataset_name" {
  description = "Name of the BigQuery dataset"
  type        = string
}

variable "location" {
  description = "Location for bucket and dataset"
  type        = string
  default     = "US"
}