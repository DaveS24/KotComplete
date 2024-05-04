import json
import requests

from datasets import Dataset


def load_jsonl_from_url(url, use_subset=False, subset_ratio=0.1):
    """
    Load a JSONL file from a URL and return its content as a list of dictionaries.
    :param url:
    :param use_subset:
    :param subset_ratio:
    :return: List of dictionaries containing the content of the JSONL file
    """
    content = []

    response = requests.get(url)
    lines = response.iter_lines(decode_unicode=True)
    for line in lines:
        data = json.loads(line)
        content.append(data)

    if use_subset:
        subset_size = int(len(content) * subset_ratio)
        content = content[:subset_size]

    return content


def create_and_tokenize_dataset(data, tokenizer):
    """
    Create a Hugging Face dataset from a list of dictionaries and tokenize it using a tokenizer.
    :param data: List of dictionaries in the format {"signature": str, "body": str}
    :param tokenizer: Hugging Face tokenizer
    :return: Hugging Face dataset
    """
    input_texts = [item["signature"] for item in data]
    target_texts = [item["body"] for item in data]

    tokenized_inputs = tokenizer(input_texts, padding=True, truncation=True, return_tensors="pt")
    tokenized_targets = tokenizer(target_texts, padding=True, truncation=True, return_tensors="pt")

    tokenized_inputs["labels"] = tokenized_targets["input_ids"]

    dataset = Dataset.from_dict({
        "input_ids": tokenized_inputs["input_ids"],
        "attention_mask": tokenized_inputs["attention_mask"],
        "labels": tokenized_inputs["labels"]
    })

    return dataset


def dataset_summary(dataset):
    """
    Print a summary of a Hugging Face dataset.
    :param dataset: Hugging Face dataset
    :return:
    """
    print("Dataset Info")
    print("============")
    print("Number of samples:", dataset.num_rows)
    print("Column names:", dataset.column_names)
    print("Features:", dataset.features)
