# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 27-04-2024

### Added

- Filepath fetching through the GitHub API
- Model-tasks extraction for each filepath


## [0.1.1] - 28-04-2024

### Added

- Strict task formatting for each model-task

### Changed

- File fetching by cloning the repository due to GitHub API limitations


## [0.2.0] - 30-04-2024

### Added

- Loading CodeXGLUE dataset
- Loading base Phi-1.5 model


## [0.2.1] - 01-05-2024

### Changed

- Saving model-tasks in JSONL files


## [0.2.2] - 02-05-2024

### Added

- Generator to load the dataset in batches
- Evaluation of the model on the CodeXGLUE test set using BLEU score


## [0.2.3] - 03-05-2024

### Added

- Duplicate elimination in the Kotlin dataset
- Train-test split for the Kotlin dataset


## [0.3.0] - 03-05-2024

### Added

- Set up the training pipeline for the model


## [0.3.1] - 03-05-2024

### Added

- Configurations for the training pipeline
- Creation of the training Dataset from the jsonl file


## [0.3.2] - 04-05-2024

### Added

- Option to train on a subset of the dataset
- Linkage to wandb for tracking the training process
- Data loading from the GitHub repository
- Src code loading from the GitHub repository