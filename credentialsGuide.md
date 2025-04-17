# API Credentials Obtaining Guide

This guide explains how to obtain **Google Cloud API credentials** and **Kaggle API credentials** required for the project. Follow the steps carefully to set up your credentials.

---

## Google Cloud API Credentials

To use Google Cloud Platform (GCP) services in the project, you need to create a GCP project and a service account with the necessary API credentials.

### Prerequisites
- A Google account (sign up at [https://accounts.google.com](https://accounts.google.com) if you don’t have one).
- Access to [Google Cloud Console](https://console.cloud.google.com/).

### Steps

1. **Create a Google Cloud Platform Project**
- Go to [https://console.cloud.google.com/](https://console.cloud.google.com/).
- Sign in with your Google account or create one. If you’re new to GCP, you’ll receive free credits to get started.
- From the GCP homepage, open the **project picker** by pressing `Command + O` (or clicking the project dropdown at the top).
- Click **NEW PROJECT**.
- Fill in a **Project name** and click **Create**.
- Once created, note the **Project ID** shown in the project picker (behind your Project name). This ID is critical for your pipeline. **Copy and save it** for later use.

2. **Create a Service Account in Google Cloud Platform**
- Ensure you’ve selected the correct project in the **project picker** (if you have multiple projects).
- Click the **hamburger icon** (top-left corner) to open the left-side panel.
- Navigate to **IAM & Admin** > **Service Accounts**.
- Click **Create service account**.
- **Service account details**: Enter a **Service account name** and click **Create and continue**.
- **Grant this service account access to project**: Assign the following roles:
- _BigQuery Admin_
- _Compute Admin_
- _Storage Admin_
- Click **Continue**.
- **Grant users access to this service account**: Leave this empty and click **Done**.

3. **Obtain the API Key**
- On the **Service Accounts** page, locate the service account you just created.
- Click the **three-dots icon** under **Actions** (on the right) and select **Manage keys**.
- Click the **Add key** dropdown (mid-left) and choose **Create new key**.
- Select **JSON** as the key type and click **Create**.
- The JSON key file (your Google Cloud Service Account API Key) will download to your computer (likely in your Downloads folder).
- **Congratulations!** Your private key is now saved. Keep this file secure and note its location for use in the project.

---

## Kaggle API Credentials

To access Kaggle datasets in the project, you need a Kaggle API token.

### Prerequisites
- A Kaggle account (sign up at [https://www.kaggle.com/](https://www.kaggle.com/) if you don’t have one).

### Steps

1. **Sign In to Kaggle**
- Go to [https://www.kaggle.com/](https://www.kaggle.com/).
- Click **Sign In** or **Register** in the top-right corner. You can sign in with a Google account for convenience.

2. **Generate and Download the API Token**
- Once logged in, click your profile picture in the top-right corner and select **Account**.
- Go to the **Settings** tab.
- Scroll down to the **API** section.
- Click **Create New Token**.
- This will download a file named `kaggle.json` (your Kaggle API key) to your computer (likely in your Downloads folder).
- Keep this file secure and note its location for use in the project.

---

### Notes
- **Security**: Do **not** share your Google Cloud JSON key or Kaggle `kaggle.json` file publicly (e.g., in your GitHub repository). Store them securely and add them to your `.gitignore` file.
- **Troubleshooting**:
- If you encounter issues in GCP, ensure you’re in the correct project and have the necessary permissions.
- For Kaggle, verify your account is active and the token is downloaded correctly.
- **Next Steps**: Refer to the project’s setup guide for instructions on using these credentials in your pipeline.

If you need further assistance, contact the project maintainer.
