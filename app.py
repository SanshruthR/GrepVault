import gradio as gr
import requests
import bs4
import re
import uuid
import csv
import time
import pandas as pd

class Hits:
    def __init__(self):
        self.mark_start_placeholder = str(uuid.uuid4())
        self.mark_end_placeholder = str(uuid.uuid4())
        self.hits = {}

    def _parse_snippet(self, snippet):
        matches = {}
        soup = bs4.BeautifulSoup(snippet, 'lxml')
        for tr in soup.select('tr'):
            line_num = tr.select("div.lineno")[0].text.strip()
            line = tr.select("pre")[0].decode_contents()
            if "<mark" not in line:
                continue
            else:
                line = re.sub(r'<mark[^<]*>',  self.mark_start_placeholder, line)
                line = line.replace("</mark>", self.mark_end_placeholder)
                line = bs4.BeautifulSoup(line, 'lxml').text
                matches[line_num] = line
        return matches

    def add_hit(self, repo, path, snippet):
        if repo not in self.hits:
            self.hits[repo] = {}
        if path not in self.hits[repo]:
            self.hits[repo][path] = {}
        for line_num, line in self._parse_snippet(snippet).items():
            self.hits[repo][path][line_num] = line

    def merge(self, hits2):
        for hit_repo, path_data in hits2.hits.items():
            if hit_repo not in self.hits:
                self.hits[hit_repo] = {}
            for path, lines in path_data.items():
                if path not in self.hits[hit_repo]:
                    self.hits[hit_repo][path] = {}
                for line_num, line in lines.items():
                    self.hits[hit_repo][path][line_num] = line

def fetch_grep_app(page, query, use_regex, whole_words, case_sensitive, repo_filter, path_filter):
    params = {
        'q': query,
        'page': page
    }
    url = "https://grep.app/api/search"

    if use_regex:
        params['regexp'] = 'true'
    elif whole_words:
        params['words'] = 'true'

    if case_sensitive:
        params['case'] = 'true'
    if repo_filter:
        params['f.repo.pattern'] = repo_filter
    if path_filter:
        params['f.path.pattern'] = path_filter
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None, None, 0
    data = response.json()
    count = data['facets']['count']
    hits = Hits()
    for hit_data in data['hits']['hits']:
        repo = hit_data['repo']['raw']
        path = hit_data['path']['raw']
        snippet = hit_data['content']['snippet']
        hits.add_hit(repo, path, snippet)

    if count > 10 * page:
        return page + 1, hits, count
    else:
        return None, hits, count

def extract_query_content(line, query):
    """
    Extracts everything after the query string until it encounters a `=`, backtick (`` ` ``), or closing double quote (`"`).
    """
    # Find the query string in the line
    query_index = line.find(query)
    if query_index == -1:
        return ""  # Query not found in the line

    # Extract everything after the query string
    remaining_line = line[query_index + len(query):]

    # Use regex to match until `=`, backtick, or closing double quote
    match = re.search(r'^([^=`"]+)', remaining_line)
    if match:
        return match.group(1).strip()
    return ""

def search_and_export(query, use_regex, whole_words, case_sensitive, repo_filter, path_filter, progress=gr.Progress()):
    hits = Hits()
    next_page = 1
    total_pages = 1
    total_results = 0
    while next_page and next_page < 101:
        progress(next_page / 100, desc="Fetching data...")
        next_page, page_hits, count = fetch_grep_app(next_page, query, use_regex, whole_words, case_sensitive, repo_filter, path_filter)
        if page_hits:
            hits.merge(page_hits)
            total_results += count
        if next_page is None:
            break
        time.sleep(1)

    # Export to CSV
    csv_filename = "search_results.csv"
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Repository", "Line Number", "Extracted Query", "Content", "Path"])  # Path moved to the end
        for repo, paths in hits.hits.items():
            for path, lines in paths.items():
                for line_num, content in lines.items():
                    extracted_query = extract_query_content(content, query)
                    writer.writerow([repo, line_num, extracted_query, content, path])  # Path moved to the end

    # Read CSV into a DataFrame for display
    df = pd.read_csv(csv_filename)
    # Filter to show only rows where `Extracted Query` is unique
    df_unique = df.drop_duplicates(subset=["Extracted Query"])
    # Limit to top 6 unique results
    df_top6_unique = df_unique.head(6)
    return csv_filename, df_top6_unique, f"**Total Results: {total_results}**", f"Displaying top 6 unique results. Download the CSV for all {total_results} results."

# Custom CSS for a modern look
custom_css = """
.gradio-container {
    font-family: 'Arial', sans-serif;
    background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
    padding: 20px;
    border-radius: 10px;
}
.gradio-header {
    text-align: center;
    font-size: 24px;
    font-weight: bold;
    color: #333;
}
.gradio-header h1 {
    text-decoration: underline;
}
.gradio-header p {
    text-decoration: underline;
}
.gradio-inputs {
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.gradio-button {
    background: #4CAF50 !important;
    color: white !important;
    border-radius: 5px !important;
    padding: 10px 20px !important;
    font-size: 16px !important;
}
.gradio-button:hover {
    background: #45a049 !important;
}
.gradio-outputs {
    background: white;
    padding: 20px;
    border-radius: 10px;
    margin-top: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.gradio-dataframe {
    max-height: 400px;
    overflow-y: auto;
    border: 1px solid #ddd;
    border-radius: 5px;
    padding: 10px;
}
.gradio-results-count {
    font-size: 18px;
    font-weight: bold;
    color: #000; /* Black color */
    margin-bottom: 10px;
}
.gradio-download-message {
    font-size: 16px;
    color: #333;
    margin-top: 10px;
}
"""

# UI using Gradio Blocks
with gr.Blocks(css=custom_css, theme="default") as demo:
    gr.Markdown("""
    <div class="gradio-header">
        <h1>GrepVault: Search Github for API Keys</h1>
        <p><a href="https://github.com/SanshruthR/GrepVault">https://github.com/SanshruthR/GrepVault</a></p>

    </div>
    """)

    with gr.Row():
        with gr.Column(scale=2, elem_classes="gradio-inputs"):
            query = gr.Textbox(label="Search Query", placeholder="Enter your search query for example :generateContent?key=", lines=1)
            use_regex = gr.Checkbox(label="Use Regular Expression", value=False)
            whole_words = gr.Checkbox(label="Match Whole Words", value=False)
            case_sensitive = gr.Checkbox(label="Case Sensitive Search", value=False)
            repo_filter = gr.Textbox(label="Repository Filter", placeholder="e.g., user/repo", lines=1)
            path_filter = gr.Textbox(label="Path Filter", placeholder="e.g., src/", lines=1)
            search_button = gr.Button("Search and Export", elem_classes="gradio-button")

        with gr.Column(scale=3, elem_classes="gradio-outputs"):
            results_count = gr.Markdown("**Total Results: 0**", elem_classes="gradio-results-count")
            csv_download = gr.File(label="Download CSV")
            csv_preview = gr.Dataframe(label="CSV Preview (Top 6 Unique Results)", headers=["Repository", "Line Number", "Extracted Query", "Content", "Path"], elem_classes="gradio-dataframe")
            download_message = gr.Markdown("Displaying top 6 unique results. Download the CSV for all results.", elem_classes="gradio-download-message")

    search_button.click(
        search_and_export,
        inputs=[query, use_regex, whole_words, case_sensitive, repo_filter, path_filter],
        outputs=[csv_download, csv_preview, results_count, download_message]
    )

demo.launch()
