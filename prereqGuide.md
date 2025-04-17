## Setup Instructions: Prerequisites Installation Guide

This section guides you through installing the required tools for the project using **Bash** on macOS. Ensure you have a terminal open to run these commands.

### Prerequisites
- **Docker & Docker Compose**: For containerization and managing multi-container applications.
- **Git**: For version control.
- **Terraform**: For infrastructure as code.
- **Kagglehub**: For accessing Kaggle datasets.

### Installation Steps

1. **Install Homebrew** (Package Manager for macOS)
- Run the following command in your terminal:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
- Follow the on-screen instructions to complete the installation. This may include adding Homebrew to your PATH.

2. **Install Terraform**
- Add the HashiCorp tap and install Terraform:
```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
```
- Verify installation:
```bash
terraform --version
```

3. **Install Kagglehub**
- Install the Kagglehub Python package:
```bash
pip install kagglehub
```
- Verify installation:
```bash
python -c "import kagglehub; print(kagglehub.__version__)"
```

4. **Install Docker, Docker Compose, and Git**
- See the **Additional** section below for terminal installation instructions.

---

## Additional: Terminal Installation for Docker, Docker Compose, and Git

These are simple terminal instructions for installing **Docker**, **Docker Compose**, and **Git** on macOS using Homebrew in **Bash**.

1. **Install Docker**
- Install Docker Desktop (which includes Docker):
```bash
brew install --cask docker
```
- After installation, open Docker Desktop from your Applications folder and follow the setup prompts.
- Verify installation:
```bash
docker --version
```

2. **Install Docker Compose**
- Docker Compose is included with Docker Desktop on macOS, so no separate installation is needed.
- Verify installation:
```bash
docker-compose --version
```

3. **Install Git**
- Install Git:
```bash
brew install git
```
- Verify installation:
```bash
git --version
```
