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

    with open(task_dir + "instructions.txt", "a") as i_file:
        i_file.write(instruction + '\n')

    with open(task_dir + "solutions.txt", "a") as s_file:
        s_file.write(solution + '\n')


def find_matches(pattern, split_char, code, task_dir):
    """
    Find matches in the provided code and save them as tasks

    :param pattern:
    :param split_char:
    :param code:
    :param task_dir:
    :return:
    """
    matches = re.findall(pattern, code)

    for match in matches:
        match = match.replace('\n', '\\n')

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

    pattern = r'if\s+[^{]*\{[^}]*\}|else\s+if\s+[^{]*\{[^}]*\}|else\s+\{[^}]*\}'
    find_matches(pattern, '{', code, task_dir)


def function_declaration_task(code, data_dir):
    """
    Extract function declaration tasks from the provided code file

    :param code:
    :param data_dir:
    :return:
    """
    task_dir = data_dir + "function_declaration_task/"

    pattern = r'fun\s+[^{}]*\{[^{}]*\}'
    find_matches(pattern, '{', code, task_dir)


def import_statement_task(code, data_dir):
    """
    Extract import statement tasks from the provided code file

    :param code:
    :param data_dir:
    :return:
    """
    task_dir = data_dir + "import_statement_task/"

    pattern = r'import\s+[^\n]*'
    find_matches(pattern, '.', code, task_dir)


def loop_statement_task(code, data_dir):
    """
    Extract loop statement tasks from the provided code file

    :param code:
    :param data_dir:
    :return:
    """
    task_dir = data_dir + "loop_statement_task/"

    pattern = r'for\s+[^{]*\{[^{]*\}|while\s+[^{]*\{[^{]*\}'
    find_matches(pattern, '{', code, task_dir)


def type_declaration_task(code, data_dir):
    """
    Extract type declaration tasks from the provided code file

    :param code:
    :param data_dir:
    :return:
    """
    task_dir = data_dir + "type_declaration_task/"

    pattern = r'var\s+[^:=]*:[^=]*|val\s+[^:=]*:[^=]*'
    find_matches(pattern, ':', code, task_dir)


def variable_declaration_task(code, data_dir):
    """
    Extract variable declaration tasks from the provided code file

    :param code:
    :param data_dir:
    :return:
    """
    task_dir = data_dir + "variable_declaration_task/"

    pattern = r'var\s+[^=]*=[^\n]*|val\s+[^=]*=[^\n]*'
    find_matches(pattern, '=', code, task_dir)


def extract_tasks(code):
    """
    Extract tasks from the provided code file

    :param code:
    :return:
    """
    data_dir = "../data/"

    conditional_statement_task(code, data_dir)
    function_declaration_task(code, data_dir)
    import_statement_task(code, data_dir)
    loop_statement_task(code, data_dir)
    type_declaration_task(code, data_dir)
    variable_declaration_task(code, data_dir)
