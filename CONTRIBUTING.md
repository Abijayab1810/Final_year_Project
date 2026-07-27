# Contributing to Smart Edge AI

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the Smart Edge AI project.

---

## Getting Started

### Prerequisites
- Python 3.8+
- Git
- Virtual environment tool (venv or conda)

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/Abijayab1810/Final_year_Project.git
cd Final_year_Project

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

---

## Development Workflow

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes
- Follow the code style guidelines in [PROFESSIONAL_STANDARDS.md](PROFESSIONAL_STANDARDS.md)
- Add type hints to all functions
- Write comprehensive docstrings
- Add tests for new functionality

### 3. Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_detector.py
```

### 4. Check Code Quality
```bash
# Format code with Black
black src/ tests/

# Lint with Flake8
flake8 src/ tests/

# Type check with mypy
mypy src/
```

### 5. Commit Changes
```bash
# Follow conventional commit format
git commit -m "feat(detector): Add dynamic tolerance for bag tracking"
```

### 6. Push and Create Pull Request
```bash
git push origin feature/your-feature-name
```

---

## Code Style Guide

### Python Standards
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Line length: Maximum 100 characters
- Use type hints for all public functions
- Use meaningful variable names

### Naming Conventions
```python
# Classes: PascalCase
class LuggageDetector:
    pass

# Functions/Methods: snake_case
def detect_bags(frame):
    pass

# Constants: UPPER_SNAKE_CASE
MOVEMENT_TOLERANCE = 20

# Private methods: _leading_underscore
def _load_model():
    pass
```

### Documentation

Every public function/class must have a docstring:

```python
def detect_bags(
    frame: np.ndarray,
    confidence: float = 0.35
) -> List[Dict[str, any]]:
    """
    Detect bags in a video frame.
    
    Args:
        frame: Input frame in BGR format.
        confidence: Detection confidence threshold.
    
    Returns:
        List of detected bags with bounding boxes.
    
    Raises:
        ValueError: If confidence not in [0, 1].
    """
```

### Type Hints
```python
from typing import List, Dict, Tuple, Optional
import numpy as np

def track_bags(
    frame: np.ndarray,
    bag_states: Dict[int, Dict],
    time_limit: int = 5
) -> Tuple[List[Dict], List[Dict]]:
    """Track bags and return detections and alerts."""
    pass
```

---

## Testing Requirements

### Test Coverage
- Minimum 80% code coverage for new features
- All public functions must have tests
- Include edge case tests

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html tests/

# Run specific test
pytest tests/test_detector.py::test_detect_bags
```

### Test Example
```python
import pytest
from src.detector import LuggageDetector

class TestLuggageDetector:
    """Test suite for LuggageDetector."""
    
    @pytest.fixture
    def detector(self):
        """Create detector for testing."""
        return LuggageDetector()
    
    def test_detect_bags(self, detector, sample_frame):
        """Test bag detection."""
        result = detector.detect_bags(sample_frame)
        assert isinstance(result, list)
```

---

## Pull Request Process

### Before Submitting PR
- [ ] Code follows style guide
- [ ] All tests pass
- [ ] Code coverage > 80%
- [ ] Docstrings added/updated
- [ ] No hardcoded values
- [ ] Commit messages follow convention

### PR Description Template
```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update

## Testing
Describe testing performed.

## Performance Impact
Any performance implications?

## Screenshots (if applicable)
Include relevant screenshots.

## Checklist
- [ ] Code follows style guide
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes
```

---

## Commit Message Guidelines

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code refactoring
- `test`: Tests
- `chore`: Build, dependencies

### Examples
```
feat(detector): Add dynamic tolerance for bag tracking
fix(api): Handle empty frame gracefully
docs(readme): Update deployment instructions
refactor(core): Extract tracking logic to separate class
test(detector): Add comprehensive test suite
```

---

## Reporting Bugs

### Bug Report Template
```markdown
## Description
Clear description of the bug.

## Steps to Reproduce
1. Step 1
2. Step 2
3. ...

## Expected Behavior
What should happen?

## Actual Behavior
What actually happens?

## Environment
- OS: [e.g., Windows 10]
- Python: [e.g., 3.10]
- Relevant Libraries: [versions]

## Additional Context
Any other information.
```

---

## Requesting Features

### Feature Request Template
```markdown
## Description
Clear description of the feature.

## Motivation
Why is this feature needed?

## Proposed Solution
How should it be implemented?

## Alternative Solutions
Other approaches considered?

## Additional Context
Screenshots, examples, references?
```

---

## Code Review Process

### Reviewer Guidelines
- Check code correctness
- Verify test coverage
- Review performance implications
- Ensure documentation is clear
- Check for security issues

### Review Checklist
- [ ] Code follows style guide
- [ ] Tests are adequate
- [ ] Documentation is clear
- [ ] No performance regression
- [ ] No security vulnerabilities

---

## Development Tips

### Useful Commands
```bash
# Format code
black src/ tests/

# Check code style
flake8 src/ tests/

# Type checking
mypy src/

# Run specific test with output
pytest -s tests/test_detector.py

# Run tests in parallel
pytest -n auto

# Generate coverage report
pytest --cov=src --cov-report=html
```

### Debugging
```python
import pdb

# Set breakpoint (Python 3.7+)
breakpoint()

# Or use older method
pdb.set_trace()

# Step through code with debugger
```

---

## Resources

- [Python Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/best-practices/)
- [YOLOv8 Documentation](https://github.com/ultralytics/ultralytics)

---

## Questions?

- Open an issue with the `question` label
- Check existing issues and discussions
- Review documentation in `/docs`

---

## Code of Conduct

- Be respectful and professional
- Welcome diverse perspectives
- Focus on constructive feedback
- Maintain a harassment-free environment

---

Thank you for contributing! 🎉
