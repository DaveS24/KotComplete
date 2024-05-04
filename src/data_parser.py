import json
import os
import random
import re
import requests

from datasets import Dataset
from tqdm import tqdm


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
                file.write(json.dumps({"signature": signature, "body": body}) + '\n')
    else:
        with open(task_file, 'w', errors='ignore') as file:
            for signature, body in tasks_dict.items():
                file.write(json.dumps({"signature": signature, "body": body}) + '\n')


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

    if match.count('FIXME'):
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

    string_literals = re.findall(r'".*?"', match)
    for string_literal in string_literals:
        match = match.replace(string_literal, '<STR_LIT>')

    number_literals = re.findall(r'-?\d+\.?\d*', match)
    for number_literal in number_literals:
        match = match.replace(number_literal, '<NUM_LIT>')

    match = match.replace('\n', '<EOL>')
    match = match.replace('    ', '<INDENT>')

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


def extract_completion_tasks(data_dir, output_dir):
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

    kotlin_files = os.listdir(data_dir)

    for task_file, task_pattern, split_char in tqdm(zip(task_files, task_patterns, split_chars), desc="Fetching tasks"):
        found_tasks = {}
        for file in kotlin_files:
            with open(data_dir + file, 'r', encoding='utf-8') as f:
                content = f.read()

            matches = find_matches(content, task_pattern)
            tasks_dict = split_signature_body(matches, split_char)

            found_tasks.update(tasks_dict)

        save_tasks(found_tasks, output_dir + task_file)

    tasks_summary(output_dir)


def tasks_summary(data_dir):
    """
    Print the summary of completion tasks

    :return:
    """
    total_tasks = 0
    for task_file in os.listdir(data_dir):
        if os.path.isdir(data_dir + task_file):
            continue

        with open(data_dir + task_file, 'r') as file:
            lines = file.readlines()
            print(task_file + ': ' + str(len(lines)))
            total_tasks += len(lines)

    print('--------------------')
    print('Total number: ' + str(total_tasks))


def split_data(data_dir, output_dir, split_ratio=0.8):
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

    tasks_summary(output_dir)


def load_and_tokenize_dataset(url, tokenizer, use_subset=False, subset_ratio=0.1):
    dataset = []

    response = requests.get(url)
    lines = response.iter_lines(decode_unicode=True)
    for line in lines:
        data = json.loads(line)
        dataset.append(data)

    if use_subset:
        subset_size = int(len(dataset) * subset_ratio)
        dataset = dataset[:subset_size]

    input_texts = [data["signature"] for data in dataset]
    target_texts = [data["body"] for data in dataset]

    tokenized_inputs = tokenizer(input_texts, padding=True, truncation=True, return_tensors="pt")
    tokenized_targets = tokenizer(target_texts, padding=True, truncation=True, return_tensors="pt")

    tokenized_inputs["labels"] = tokenized_targets["input_ids"]

    dataset = Dataset.from_dict({
        "input_ids": tokenized_inputs["input_ids"],
        "attention_mask": tokenized_inputs["attention_mask"],
        "labels": tokenized_inputs["labels"]
    })

    return dataset


def display_dataset_info(dataset):
    print("Dataset Info")
    print("============")
    print("Number of samples:", dataset.num_rows)
    print("Column names:", dataset.column_names)
    print("Features:", dataset.features)
