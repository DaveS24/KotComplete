import json
import os
import re


def save_tasks(tasks_dict, task_file):
    """
    Save the provided tasks dictionary to the provided task file

    :param tasks_dict:
    :param task_file:
    :return:
    """
    if os.path.exists(task_file):
        with open(task_file, 'a', errors='ignore') as file:
            for signature, body in tasks_dict.items():
                file.write('{"signature": "' + signature + '", "body": "' + body + '"}\n')
    else:
        with open(task_file, 'w', errors='ignore') as file:
            for signature, body in tasks_dict.items():
                file.write('{"signature": "' + signature + '", "body": "' + body + '"}\n')


def split_signature_body(matches, split_char):
    """
    Split the signature and body of the provided matches

    :param matches:
    :param split_char:
    :return:
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


def filter_invalid(match):
    """
    Filter out invalid matches

    :param match:
    :return:
    """
    if len(match) > 500:
        return None

    if match.count('\n') > 10:
        return None

    if match.count('{') != match.count('}'):
        return None

    if match.count('TODO'):
        return None

    if match.count('DEBUG'):
        return None

    return match


def format_match(match):
    """
    Format the provided match

    :param match:
    :return:
    """
    if filter_invalid(match) is None:
        return None

    comments = re.findall(r'//.*?(\n|$)', match, re.DOTALL)
    for comment in comments:
        match = match.replace(comment, '')

    multiline_comments = re.findall(r'/\*.*?\*\*?/', match, re.DOTALL)
    for comment in multiline_comments:
        match = match.replace(comment, '')

    match = match.replace('\n', '\\n')
    match = match.replace('    ', '')

    return match


def find_matches(code, patterns):
    """
    Find all matches in the provided code

    :param code:
    :param patterns:
    :return:
    """
    all_matches = []

    for pattern in patterns:
        matches = re.findall(pattern, code)

        for match in matches:
            match = format_match(match)

            if match is None:
                continue

            all_matches.append(match)

    return all_matches


def extract_completion_tasks(code):
    """
    Extract completion tasks from the provided code

    :param code:
    :return:
    """
    data_dir = "../data/Kotlin/completion_tasks/"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    task_files = ["condition_tasks.jsonl",
                  "function_tasks.jsonl",
                  "import_tasks.jsonl",
                  "loop_tasks.jsonl",
                  "variable_tasks.jsonl"]

    task_patterns = [[re.compile(r'if\s*\([^{}\n]*?\)\s*\{.*?}', re.DOTALL),            # if statement
                      re.compile(r'else\s+if\s*\([^{}\n]*?\)\s*\{.*?}', re.DOTALL),     # else if statement
                      re.compile(r'else\s*\{.*?}', re.DOTALL),                          # else statement
                      re.compile(r'when\s*\([^{}\n]*?\)\s*\{.*?}', re.DOTALL)],         # when statement

                     [re.compile(r'fun\s+\w+\s*\([^{}=]*?\)\s*\{.+?}', re.DOTALL)],     # function declaration

                     [re.compile(r'import\s+.*?\n'),                                            # import statement
                      re.compile(r'package\s+.*?\n')],                                          # package statement

                     [re.compile(r'for\s*\([^{}\n]*?\)\s*\{[^{}]*}', re.DOTALL),        # for loop
                      re.compile(r'while\s*\([^{}\n]*?\)\s*\{[^{}]*}', re.DOTALL)],     # while loop

                     [re.compile(r'var\s+\w+\s*=\s*.*\n'),                                      # var declaration
                      re.compile(r'val\s+\w+\s*=\s*.*\n')]                                      # val declaration
                     ]

    split_chars = ['{', '{', '.', '{', '=']

    for task_file, task_pattern, split_char in zip(task_files, task_patterns, split_chars):
        matches = find_matches(code, task_pattern)
        tasks_dict = split_signature_body(matches, split_char)
        save_tasks(tasks_dict, data_dir + task_file)


def tasks_summary():
    """
    Print the summary of completion tasks

    :return:
    """
    data_dir = "../data/Kotlin/completion_tasks/"

    total_tasks = 0
    for task_file in os.listdir(data_dir):
        with open(data_dir + task_file, 'r') as file:
            lines = file.readlines()
            print(task_file + ': ' + str(len(lines)))
            total_tasks += len(lines)

    print('--------------------')
    print('Total number: ' + str(total_tasks))


def load_dataset(file_path, batch_size):
    """
    Generator to load the dataset in batches

    :param file_path:
    :param batch_size:
    :return:
    """
    with open(file_path, 'r') as file:
        dataset = [json.loads(line) for line in file]

        for i in range(0, len(dataset), batch_size):
            tasks = dataset[i:i + batch_size]
            instruction = [task['signature'] for task in tasks]
            target = [task['body'] for task in tasks]

            yield instruction, target
