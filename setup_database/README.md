# Setup Database

This directory contains the necessary files to set up the database using Docker Compose.

## Prerequisites

- Docker
- Docker Compose
- Kaggle API credentials (`kaggle.json`)

## Instructions

1. **Download Kaggle API credentials:**
    - Go to your Kaggle account settings.
    - Scroll down to the "API" section and click on "Create New API Token".
    - This will download a file named `kaggle.json`.

2. **Place `kaggle.json` in the current directory:**
    - Move the downloaded `kaggle.json` file to this directory (`text2sql/setup_database/`).

3. **Run Docker Compose:**
    - Open a terminal and navigate to this directory.
    - Run the following command to start the services defined in the `docker-compose.yml` file:
      ```sh
      docker compose up
      ```

This will set up and run the database container as defined in the `docker-compose.yml` file.