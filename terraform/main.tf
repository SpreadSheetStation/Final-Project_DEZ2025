terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
    }
  }
}

provider "google" {
  credentials = file(var.credentials)
  project     = var.project
  region      = var.region
}

resource "google_storage_bucket" "crypto_bucket" {
  name     = var.gcs_bucket_name
  location = var.location
}

resource "google_bigquery_dataset" "crypto_dataset" {
  dataset_id = var.bq_dataset_name
  location   = var.location
}