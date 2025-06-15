# Guidelines for Codex Agents

## Overview
This repository contains Python scripts and documents for converting various 3D
asset formats to USD or USDZ, plus sample scripts and tests. The tools target
Python 3.10.

## Coding Conventions
- Use four spaces for indentation in Python files.
- Keep code compatible with Python 3.10.
- Follow the existing file structure when adding new modules or tests.

## Running Tests
- Install dependencies (if not already available) with:
  ```bash
  pip install usd-core numpy pytest
  ```
- Execute the test suite from the repository root using `pytest`.
  All code changes should keep the tests passing.

## Commit Guidelines
- Write clear, concise commit messages in the imperative mood, e.g.
  "Add MaterialX flag to parser".
- Ensure each commit leaves the repository in a working state with all tests
  passing.

## Documentation
- When modifying code that affects the documented behaviour, update or add Chinese-language docs in
  that folder as needed.

