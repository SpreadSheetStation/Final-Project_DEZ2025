from google.cloud import storage

def upload_csv():
    client = storage.Client()
    bucket = client.get_bucket("bitcoin-data-bucket-2025")
    blob = bucket.blob("raw/btc_1d_data_2018_to_2025.csv")
    blob.upload_from_filename("/Users/neogami/Desktop/Final-Project_DEZ2025/Final-Project_DEZ2025/btc_1d_data_2018_to_2025.csv")
    print("CSV uploaded!")

if __name__ == "__main__":
    upload_csv()