import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import curses

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

    matched_files = {}
    content_name_array = content_name.lower().split()
    threshold = len(content_name_array) / 2  # At least half of the elements

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_directory = {executor.submit(fetch_files_in_directory, base_url + directory, session, accepted_extensions): directory for directory in directories}
        for future in as_completed(future_to_directory):
            directory = future_to_directory[future]
            try:
                files = future.result()
                # Check if the directory name contains at least half of the content_name_array words
                match_count = sum(content.lower() in directory.lower() for content in content_name_array)
                if match_count >= threshold:
                    matched_files[directory] = files
            except Exception as exc:
                print(f'Error fetching directory contents for {directory}: {exc}')

    # Call the curses wrapper function to start the CLI
    curses.wrapper(directory_selection_cli, matched_files)

def directory_selection_cli(stdscr, matched_files):
    curses.curs_set(0)  # Hide the cursor
    directories = list(matched_files.keys())
    selected = [False] * len(directories)
    current_row = 0

    def print_menu():
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        for idx, directory in enumerate(directories):
            x = w // 2 - len(directory) // 2
            y = h // 2 - len(directories) // 2 + idx
            if idx == current_row:
                stdscr.attron(curses.color_pair(1))
            if selected[idx]:
                stdscr.addstr(y, x, directory + " [*]")
            else:
                stdscr.addstr(y, x, directory)
            if idx == current_row:
                stdscr.attroff(curses.color_pair(1))
        stdscr.refresh()

    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    while True:
        print_menu()
        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(directories) - 1:
            current_row += 1
        elif key == ord(' '):
            selected[current_row] = not selected[current_row]
        elif key == ord('\n'):
            break

    stdscr.clear()
    selected_directories = {directories[i]: matched_files[directories[i]] for i in range(len(directories)) if selected[i]}
    stdscr.addstr(0, 0, "Selected directories and files:")
    row = 1
    for directory, files in selected_directories.items():
        stdscr.addstr(row, 0, directory)
        row += 1
        for file in files:
            stdscr.addstr(row, 2, file)
            row += 1
    stdscr.refresh()
    stdscr.getch()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Crawl directories and list files with accepted extensions.')
    parser.add_argument('url', type=str, help='The base URL of the directory to crawl')
    parser.add_argument('content', type=str, help='Name of the content to find')

    args = parser.parse_args()

    main(args.url, args.content)
