# GrepVault - Search GitHub for API Keys
![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Gradio](https://img.shields.io/badge/Gradio-3.1.4-blueviolet?style=for-the-badge&logo=gradio&logoColor=white)
![Deployed on Hugging Face](https://img.shields.io/badge/Deployed%20on-Hugging%20Face-yellow?style=for-the-badge&logo=huggingface&logoColor=white)
![MIT License](https://img.shields.io/badge/License-MIT-008080?style=for-the-badge&logo=open-source-initiative&logoColor=white)
![GrepVault 1.0](https://img.shields.io/badge/GrepVault%201.0-vibrant%20blue?style=for-the-badge&logo=github&logoColor=white)

![e6af2a3ea4f0a71d86 gradio live_](https://github.com/user-attachments/assets/bdec6ee4-3736-437b-b2bc-a3f6c2388466)




## Overview

**GrepVault** is a tool designed to search GitHub repositories for potential API keys or sensitive information using advanced text search and regex capabilities. It integrates with the GitHub to fetch search results and displays them in a user-friendly interface built with Gradio. Users can easily search through large amounts of code, extract sensitive data, and export the results in a CSV format for further analysis.

## Features

- **Text Search**: Perform keyword-based search for potential API keys and other sensitive information.
- **Regex Search**: Utilize regular expressions for more advanced and precise searches.
- **CSV Export**: Export the search results to a CSV file for further processing or record-keeping.
- **Real-Time Progress**: The Gradio interface displays real-time progress of the search process.
- **Custom Filters**: Apply filters based on repository name, path, and case sensitivity to narrow down results.

## How It Works

1. **User Input**: Users enter a search query along with optional filters like case sensitivity, regular expression, and repository or path filters.
2. **Fetching Data**: The tool queries the GitHub API to fetch relevant code snippets based on the query.
3. **Displaying Results**: The results are displayed in real-time using Gradio's interactive interface. Users can see a summary of the top results.
4. **Exporting Results**: The results are exported to a CSV file, including the repository, line number, extracted query, content, and path.

## Usage

1. Clone the repository and install the dependencies:
    ```bash
    git clone https://github.com/SanshruthR/GrepVault.git
    cd GrepVault
    pip install -r requirements.txt
    ```

2. Run the script:
    ```bash
    python app.py
    ```

3. Use the Gradio interface to enter a search query and apply filters:
    - **Text Search**: Enter a keyword or API key to search for.
    - **Regex Search**: Enable regex to perform complex search patterns.
    - **Export Results**: Once the search is complete, download the results in CSV format.

### Deployment

This project is deployed on **Hugging Face Spaces**. You can interact with the app via the following link:

[Live Demo on Hugging Face](https://huggingface.co/spaces/Sanshruth/GrepVault)

## License

This project is licensed under the MIT License.
