# Scraper Project

Welcome to the Scraper Project! This repository contains the code for a web scraping and Q&A application that leverages large language models (LLMs).

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Run from Streamlit Community Environment](#run-from-streamlit-community-environment)
- [Run from Local](#run-from-local)
- [Usage](#usage)
- [Python Packages](#python-packages)
- [Contributing](#contributing)
- [License](#license)

## Overview
The Scraper Project is a Streamlit app designed to facilitate web scraping, data storage, and question answering using LLMs for natural language processing and vector indexing. It employs a Retrieve and Generate (RAG) model, utilizing the powerful llama-index for vector indexing and retrieval.

## Key Features
- **Easy-to-Use Interface**: Provides a simple and intuitive interface for inputting URLs and asking questions.
- **Automated Web Scraping**: Uses Playwright to scrape text content from specified web pages, adhering to site rules by checking `robots.txt`.
- **Intelligent Q&A**: Employs a RAG architecture, integrating scraping with question-answering capabilities using the llama-index package.
- **Secure and Private**: Ensures that all data handling and storage adhere to best practices for security and privacy.

## Run from Streamlit Community Environment
The application is hosted at [https://scraper-web.streamlit.app/](https://scraper-web.streamlit.app/).

## Run from Local
To run the Scraper Project locally, follow these steps:

1. **Create a virtual Python environment**:
    ```bash
    python -m venv env
    source env/bin/activate
    ```

2. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/scraper-project.git
    cd scraper-project
    ```

3. **Set up the environment**:
    Install the necessary libraries and tools by running:
    ```bash
    pip install -r requirements.txt
    ```

4. **Run the project**:
    ```bash
    streamlit run main.py
    ```

## Usage
To use the Scraper Project, follow these steps:

1. **Run the Streamlit application**:
    ```bash
    streamlit run main.py
    ```

2. **Input URL**:
    - Enter the URL of the website you want to scrape in the provided input field.
    - Click the button to start the scraping process.

3. **Select the Website Language**:
    - Choose the appropriate language to ensure the correct embedding model is used.

4. **Ask Questions**:
    - After scraping, enter your question in the input field.
    - The application retrieves relevant information, creates a context, sends the question and context to the LLM, and provides an answer.

## Python Packages
This project primarily uses the following Python packages:
- **Streamlit**: For creating the web application.
- **Playwright**: For automated web scraping.
- **llama-index**: For the RAG implementation, handling vector indexing and retrieval.

## Contributing
We welcome contributions to the Scraper Project! To contribute, follow these steps:

1. **Fork the repository**.
2. **Create a new branch**:
    ```bash
    git checkout -b feature/your-feature-name
    ```
3. **Make your changes and commit them**:
    ```bash
    git commit -m "Add your feature description"
    ```
4. **Push to the branch**:
    ```bash
    git push origin feature/your-feature-name
    ```
5. **Create a pull request**.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
