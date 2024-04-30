import os
import re


def save_task(task_dir, instruction, solution):
    """
    Save the provided task instruction and solution to the specified directory

    :param task_dir:
    :param instruction:
    :param solution:
    :return:
    """
    if not os.path.exists(task_dir):
        os.makedirs(task_dir)

    with open(task_dir + "instructions.txt", "a", errors='ignore') as i_file:
        i_file.write(instruction + '\n')

    with open(task_dir + "solutions.txt", "a", errors='ignore') as s_file:
        s_file.write(solution + '\n')


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


def find_matches(patterns, split_char, code, task_dir):
    """
    Find matches in the provided code and save them as tasks

    :param patterns:
    :param split_char:
    :param code:
    :param task_dir:
    :return:
    """
    for pattern in patterns:
        matches = re.findall(pattern, code)

        for match in matches:
            match = format_match(match)

            if match is None:
                continue

            parts = match.split(split_char)
            instruction = parts[0] + split_char
            solution = split_char.join(parts[1:])

            save_task(task_dir, instruction, solution)


def conditional_statement_task(code, data_dir):
    """
    Extract conditional statement tasks from the provided code file

    :param code:
    :param data_dir:
    :return:
    """
    task_dir = data_dir + "conditional_statement_task/"

    if_pattern = re.compile(r'if\s*\([^{}\n]*?\)\s*\{.*?}', re.DOTALL)
    else_if_pattern = re.compile(r'else\s+if\s*\([^{}\n]*?\)\s*\{.*?}', re.DOTALL)
    else_pattern = re.compile(r'else\s*\{.*?}', re.DOTALL)
    when_pattern = re.compile(r'when\s*\([^{}\n]*?\)\s*\{.*?}', re.DOTALL)

    patterns = [if_pattern, else_if_pattern, else_pattern, when_pattern]
    find_matches(patterns, '{', code, task_dir)


def function_declaration_task(code, data_dir):
    """
    Extract function declaration tasks from the provided code file

    :param code:
    :param data_dir:
    :return:
    """
    task_dir = data_dir + "function_declaration_task/"

    fun_pattern = re.compile(r'fun\s+\w+\s*\([^{}=]*?\)\s*\{.+?}', re.DOTALL)

    patterns = [fun_pattern]
    find_matches(patterns, '{', code, task_dir)


def import_statement_task(code, data_dir):
    """
    Extract import statement tasks from the provided code file

    :param code:
    :param data_dir:
    :return:
    """
    task_dir = data_dir + "import_statement_task/"

    import_pattern = re.compile(r'import\s+.*?\n')
    package_pattern = re.compile(r'package\s+.*?\n')

    patterns = [import_pattern, package_pattern]
    find_matches(patterns, '.', code, task_dir)


def loop_statement_task(code, data_dir):
    """
    Extract loop statement tasks from the provided code file

    :param code:
    :param data_dir:
    :return:
    """
    task_dir = data_dir + "loop_statement_task/"

    for_pattern = re.compile(r'for\s*\([^{}\n]*?\)\s*\{[^{}]*}', re.DOTALL)
    while_pattern = re.compile(r'while\s*\([^{}\n]*?\)\s*\{[^{}]*}', re.DOTALL)

    patterns = [for_pattern, while_pattern]
    find_matches(patterns, '{', code, task_dir)


def variable_declaration_task(code, data_dir):
    """
    Extract variable declaration tasks from the provided code file

    :param code:
    :param data_dir:
    :return:
    """
    task_dir = data_dir + "variable_declaration_task/"

    var_pattern = re.compile(r'var\s+\w+\s*=\s*.*\n')
    val_pattern = re.compile(r'val\s+\w+\s*=\s*.*\n')

    patterns = [var_pattern, val_pattern]
    find_matches(patterns, '=', code, task_dir)


def extract_tasks(code):
    """
    Extract tasks from the provided code file

    :param code:
    :return:
    """
    data_dir = "../data/model_tasks/"

    conditional_statement_task(code, data_dir)
    function_declaration_task(code, data_dir)
    import_statement_task(code, data_dir)
    loop_statement_task(code, data_dir)
    variable_declaration_task(code, data_dir)
