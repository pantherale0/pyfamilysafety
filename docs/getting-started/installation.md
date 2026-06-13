# Installation

Install **pyfamilysafety** from PyPI:

```bash
pip install pyfamilysafety
```

## Development install

Clone the repository and install with development dependencies:

```bash
git clone https://github.com/pantherale0/pyfamilysafety.git
cd pyfamilysafety
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

## Dependencies

Runtime dependencies:

| Package | Purpose |
| --- | --- |
| `aiohttp` | Async HTTP client for Microsoft APIs |
| `python-dateutil` | Timezone handling for API timestamps |

Python **3.8+** is required.

## Verify installation

```python
import pyfamilysafety
print(pyfamilysafety.__version__)
```

Next: [Authentication](authentication.md)
