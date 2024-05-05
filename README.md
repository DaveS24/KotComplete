# KotComplete: Improving Language Model Completion for Kotlin

Welcome to KotComplete, where I (try to) take Kotlin code completion to the next level!  
This project aims to enhance Language Model (LM) capabilities for underrepresented programming languages, focusing primarily on Kotlin.

> **To run the code**, open the notebooks in Google Colab or a similar environment and follow the instructions provided.

## Overview

The project is split up into three main notebooks and two source files to streamline the development process.  
Here's a brief overview of each component:

### Notebooks:

> [prepare_data.ipynb](https://github.com/DaveS24/KotComplete/blob/main/notebooks/prepare_data.ipynb)
>
> This notebook outlines the process of creating the Kotlin dataset for training and evaluation.  
> I start by cloning the Kotlin repository and using a simple Python script (not included in this repository) to extract all Kotlin files. I then utilize the [kotlin_data_parser.py](https://github.com/DaveS24/KotComplete/blob/main/src/kotlin_data_parser.py) code to load the contents of these files, extract tasks using regex patterns, and split them into [instruction, target] pairs. Finally, I save these pairs in .jsonl files and create train.jsonl and test.jsonl files through a train-test-split process.

> [fine_tuning_pipeline.ipynb](https://github.com/DaveS24/KotComplete/blob/main/notebooks/fine_tuning_pipeline.ipynb)
>
> Here, I delve into the fine-tuning process of the Language Model using the Phi-1.5 model architecture.  
> I load the base model and tokenizer with modified settings for faster processing, utilize the [dataset_loader.py](https://github.com/DaveS24/KotComplete/blob/main/src/dataset_loader.py) code to create a dataset object from the train.jsonl file, and train it using the Trainer module. The progress and results are logged to WandB, and the tuned model is saved to Google Drive for future use.

> [model_analysis.ipynb](https://github.com/DaveS24/KotComplete/blob/main/notebooks/model_analysis.ipynb)
>
> In this notebook, I analyze the performance of both the base and tuned models on the evaluation datasets.  
> I begin by loading the pretrained model files from my GitHub repository, create the models (base and tuned) and tokenizer, and evaluate on both the Kotlin test.jsonl file and CodeXGLUE method-completion test set. The results are logged to WandB for easier comparison.

### Source Files:

> [data_parser.py](https://github.com/DaveS24/KotComplete/blob/main/src/kotlin_data_parser.py): Contains functions to extract, format and save completion tasks from Kotlin files, as well as split them into train and test sets.  
> [dataset_loader.py](https://github.com/DaveS24/KotComplete/blob/main/src/dataset_loader.py): Contains functions to load the data from the .jsonl files, tokenize it, and create a dataset object.