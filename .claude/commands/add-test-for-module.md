---
description: Add comprehensive unit tests for the specified Python source code file. Example: `/add-test-for-module /path/to/s3vectorm/math_ops.py comprehensive "optional additional requirements"`
allowed-tools: Write(s3vectorm/**/*.py), Write(tests/**/*.py), Bash(.venv/bin/python tests/**/*.py)
---

## Your Task
Add unit test for "$ARGUMENTS" and use $ARGUMENTS mode (default to "normal" if not specified). Additional requirements (may be empty): $ARGUMENTS

## Test Strategy
- Follow the ".claude/md/Python-test-strategy-instruction.md" document to locate the correct unit test file location
- Create new test file if it doesn't exist, update existing file if present
- If test file exists, analyze it to identify outdated or missing test coverage
- Use `git` command when needed to identify recent changes in the source code
- Follow the pattern in "tests/test_api.py" to use `run_cov_test` property in `if __name__ == "__main__":` block
- Run the test file after creation/update to verify functionality

## Test Modes
**Simple Mode**: 
- Add basic unit tests to ensure code execution coverage
- Use meaningful test data when possible, simple mock data when necessary
- Primary goal: increase code coverage

**Normal Mode**: 
- Use meaningful data to cover most code logic branches
- Ensure code works well in common scenarios
- Include simple, common edge cases without overcomplicating

**Comprehensive Mode**: 
- Use meaningful data to cover ALL code logic branches
- Ensure code works correctly in all scenarios
- Include complex edge case testing for thorough coverage
