# Scraper Project

Welcome to the Scraper Project! This repository contains the code for a web scraping and Q&A application that leverages LLM's and embedding API to scrape websites, store data in a vector database, and answer user queries.

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Overview
The Scraper Project is designed to facilitate web scraping, data storage, and question answering, and LLM's for natural language processing. This application allows users to input a URL, scrape relevant content, store the data as embeddings, and retrieve answers to questions based on the scraped data.

## Key Features
- **Easy-to-Use Interface**: Provides a simple and intuitive interface for inputting URLs and asking questions.
- **Automated Web Scraping**: Automatically scrapes text content from specified web pages.
- **Intelligent Q&A**: Uses advanced AI models to answer questions based on the scraped content.
- **Secure and Private**: Ensures that all data handling and storage adheres to security and privacy best practices.

## Installation
To get started with the Scraper Project, follow these steps:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/scraper-project.git
    cd scraper-project
    ```

2. **Set up the environment**:
    Install the necessary libraries and tools by running:
    ```bash
    pip install streamlit requests beautifulsoup4 selenium webdriver-manager pandas faiss-cpu openai
    ```

3. **Set up the project**:
    Prepare the development environment by creating the required files:
    ```bash
    touch streamlit_app.py
    ```

## Usage
To use the Scraper Project, follow these steps:

1. **Run the Streamlit application**:
    ```bash
    streamlit run streamlit_app.py
    ```

2. **Input URL**:
    - Enter the URL of the website you want to scrape in the provided input field.
    - Click the button to start the scraping process. The application will show status messages to inform you about the progress.

3. **Ask Questions**:
    - After scraping, enter your question in the input field provided.
    - The application will retrieve relevant information from the vector database and provide an answer.

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
