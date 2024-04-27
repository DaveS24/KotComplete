import base64
import os
import requests

from data_parser import extract_tasks
from tqdm import tqdm

REPO_OWNER = "JetBrains"
REPO_NAME = "kotlin"
PERSONAL_ACCESS_TOKEN = os.environ.get("GITHUB_ACCESS_TOKEN")


def setup():
    """
    Set up the base URL and headers for the GitHub API

    :return:
    """
    base_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/"

    headers = {}
    if PERSONAL_ACCESS_TOKEN:
        headers["Authorization"] = f"token {PERSONAL_ACCESS_TOKEN}"

    return base_url, headers


def fetch_kotlin_paths(base_url, headers):
    """
    Fetch file paths with the specified extension from the provided repository

    :param base_url:
    :param headers:
    :return:
    """
    file_extension = ".kt"
    call_counter = 0

    def search_files(url, paths_txt):
        """
        Recursively search for files with the specified extension in the provided repository

        :param url:
        :param paths_txt:
        :return:
        """
        nonlocal call_counter
        call_counter += 1

        # Progress indicator
        if call_counter % 100 == 0:
            print(f"{call_counter}: {url}")

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Recursively step through directories to extract file paths with the specified extensions
        contents = response.json()
        for item in contents:
            if item["type"] == "file":
                if item["name"].endswith(file_extension):
                    file_path = item["path"]
                    paths_txt.write(file_path + "\n")

            elif item["type"] == "dir":
                search_files(item["url"], paths_txt)

    # Write file paths to kotlin_filepaths.txt
    with open("../data/filepaths.txt", "w") as file:
        search_files(base_url, file)


def fetch_data(file_paths, base_url, headers):
    """
    Fetch content from the specified file paths through the GitHub API

    :param file_paths:
    :param base_url:
    :param headers:
    :return:
    """
    for file_path in tqdm(file_paths, desc="Fetching data"):
        url = f"{base_url}{file_path}"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            # Decode content from base64
            content = response.json().get("content")
            file_content = base64.b64decode(content).decode("utf-8")

            # Extract important data from the file content
            extract_tasks(file_content)

        except Exception as e:
            # Log errors and continue fetching data
            with open("../data/error_log.txt", "a") as log_file:
                log_file.write(f"{e}: {url}\n")
            continue
