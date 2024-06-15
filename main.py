import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse

def get_authenticated_session():
    session = requests.Session()
    return session

def fetch_directory_contents(url, session):
    response = session.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.content, 'html.parser')

def list_directories(base_url, session):
    soup = fetch_directory_contents(base_url, session)
    directories = [a.get('href') for a in soup.find_all('a') if a.get('href').endswith('/')]
    return directories

def fetch_files_in_directory(directory_url, session, accepted_extensions):
    soup = fetch_directory_contents(directory_url, session)
    files = [a.get('href') for a in soup.find_all('a') if any(a.get('href').lower().endswith(ext) for ext in accepted_extensions)]
    return [directory_url + file for file in files]

def main(base_url, content_name):
    accepted_extensions = ['.mp4', '.mkv', '.avi']  # Add your accepted extensions here
    max_workers = 5  # Adjust the number of concurrent workers as needed

    session = get_authenticated_session()
    directories = list_directories(base_url, session)

    files = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_directory = {executor.submit(fetch_files_in_directory, base_url + directory, session, accepted_extensions): directory for directory in directories}
        for future in as_completed(future_to_directory):
            try:
                files.extend(future.result())
            except Exception as exc:
                print(f'Error fetching directory contents: {exc}')

    # We split the input string for the content name to make it case-insensitive
    content_name_array = content_name.lower().split()
    threshold = len(content_name_array) / 2  # At least half of the elements

    for file in files:
        match_count = sum(content.lower() in file.lower() for content in content_name_array)
        if match_count >= threshold:
            print(file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Crawl directories and list files with accepted extensions.')
    parser.add_argument('url', type=str, help='The base URL of the directory to crawl')
    parser.add_argument('content', type=str, help='Name of the content to find')

    args = parser.parse_args()

    main(args.url, args.content)
