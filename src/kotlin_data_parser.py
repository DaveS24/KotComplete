import json
import os
import random
import re


def get_extraction_setup():
    """
    Returns the regex patterns and split characters for extracting different types of tasks from Kotlin code.
    :return: Regex patterns and split characters
    """
    task_patterns = {
        'condition': [
            re.compile(r'if\s*\([^{}\n]*?\)\s*\{.*?}', re.DOTALL),
            re.compile(r'else\s+if\s*\([^{}\n]*?\)\s*\{.*?}', re.DOTALL),
            re.compile(r'else\s*\{.*?}', re.DOTALL),
            re.compile(r'when\s*\([^{}\n]*?\)\s*\{.*?}', re.DOTALL)
        ],
        'function': [
            re.compile(r'fun\s+\w+\s*\([^{}=]*?\)\s*\{.+?}', re.DOTALL)
        ],
        'import': [
            re.compile(r'import\s+.*?\n'),
            re.compile(r'package\s+.*?\n')
        ],
        'loop': [
            re.compile(r'for\s*\([^{}\n]*?\)\s*\{[^{}]*}', re.DOTALL),
            re.compile(r'while\s*\([^{}\n]*?\)\s*\{[^{}]*}', re.DOTALL)
        ],
        'variable': [
            re.compile(r'var\s+\w+\s*=\s*.*\n'),
            re.compile(r'val\s+\w+\s*=\s*.*\n')
        ]
    }

    split_chars = ['{', '{', '.', '{', '=']

    return task_patterns, split_chars


def validity_check(match):
    """
    Checks if the given match is valid by checking various conditions.
    :param match: Match to check
    :return: True if the match is valid, False otherwise
    """
    if len(match) > 1000:
        return False

    if match.count('\n') > 10:
        return False

    if match.count('{') != match.count('}'):
        return False

    if match.count('(') != match.count(')'):
        return False

    if 'TODO' in match or 'DEBUG' in match or 'FIXME' in match:
        return False

    return True


def format_match(match):
    """
    Formats the given match by replacing literals and removing comments.
    :param match: Match to format
    :return: Formatted match
    """
    match = re.sub(r'//.*?(\n|$)', '', match, flags=re.DOTALL)
    match = re.sub(r'/\*.*?\*\*?/', '', match, flags=re.DOTALL)

    match = re.sub(r'"(.*?)"', r'<STR_LIT>', match)
    match = re.sub(r'-?\d+\.?\d*', r'<NUM_LIT>', match)

    match = match.replace('\n', '<EOL>')
    match = match.replace('    ', '<INDENT>')

    return match


def find_and_filter_matches(content, patterns):
    """
    Finds all matches of the given patterns in the content, formats them and filters out invalid matches.
    :param content: Code to search for matches
    :param patterns: List of regex patterns to search for
    :return: List of valid and formatted matches
    """
    matches_list = []
    for pattern in patterns:
        matches = re.findall(pattern, content)

        for match in matches:
            if not validity_check(match):
                continue

            formatted_match = format_match(match)
            matches_list.append(formatted_match)

    return matches_list


def split_task_parts(matches, split_char):
    """
    Splits the given matches into signature and body parts using the given split character.
    :param matches: List of matches to split
    :param split_char: Character to split the matches
    :return: Dictionary containing signature and body parts of the matches
    """
    tasks_dict = {}
    for match in matches:
        parts = match.split(split_char)

        signature = parts[0] + split_char
        signature = signature.strip()

        body = split_char.join(parts[1:])
        body = body.strip()

        tasks_dict[signature] = body

    return tasks_dict


def save_to_jsonl(tasks, path):
    """
    Saves the given tasks as a jsonl file.
    :param tasks: Dictionary containing tasks
    :param path: Path to save the tasks
    :return:
    """
    if os.path.exists(path):
        with open(path, 'a', errors='ignore') as file:
            for signature, body in tasks.items():
                file.write(json.dumps({"signature": signature, "body": body}) + '\n')
    else:
        with open(path, 'w', errors='ignore') as file:
            for signature, body in tasks.items():
                file.write(json.dumps({"signature": signature, "body": body}) + '\n')


def extract_and_save_completion_tasks(data_dir, output_dir):
    """
    Extracts Kotlin code completion tasks from the given data directory and saves them as jsonl files.
    :param data_dir: Directory containing Kotlin code files
    :param output_dir: Directory to save the extracted tasks
    :return:
    """
    task_patterns, split_chars = get_extraction_setup()

    data_files = os.listdir(data_dir)
    for task_type, task_patterns, split_char in zip(task_patterns.keys(), task_patterns.values(), split_chars):
        tasks_dict = {}
        for file in data_files:
            with open(data_dir + file, 'r', encoding='utf-8') as f:
                content = f.read()

            matches = find_and_filter_matches(content, task_patterns)
            tasks = split_task_parts(matches, split_char)

            tasks_dict.update(tasks)

        output_path = output_dir + task_type + '_tasks.jsonl'
        save_to_jsonl(tasks_dict, output_path)


def tasks_summary(tasks_dir):
    """
    Prints the number of tasks in each file and the total number of tasks in the given data directory.
    :param tasks_dir: Directory containing jsonl files of tasks
    :return:
    """
    total_tasks = 0
    for file in os.listdir(tasks_dir):
        if os.path.isdir(tasks_dir + file):
            continue

        with open(tasks_dir + file, 'r') as f:
            tasks = f.readlines()
            total_tasks += len(tasks)

            print(f'{file}: {len(tasks)}')

    print(f'Total # of tasks: {total_tasks}')


def train_test_split(data_dir, output_dir, split_ratio=0.8):
    """
    Splits the data in the given directory into training and testing sets based on the given split ratio.
    :param data_dir: Directory containing jsonl files of tasks
    :param output_dir: Directory to save the training and testing sets
    :param split_ratio: Ratio of training data
    :return:
    """
    combined_data = []
    for task_file in os.listdir(data_dir):
        with open(data_dir + task_file, 'r') as file:
            data = [json.loads(line) for line in file]
            combined_data.extend(data)

    random.shuffle(combined_data)

    split_index = int(split_ratio * len(combined_data))
    train_data = combined_data[:split_index]
    test_data = combined_data[split_index:]

    with open(output_dir + 'train.jsonl', 'w') as file:
        for item in train_data:
            file.write(json.dumps(item) + '\n')

    with open(output_dir + 'test.jsonl', 'w') as file:
        for item in test_data:
            file.write(json.dumps(item) + '\n')
