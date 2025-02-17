ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION}

# Set the project root as the Python module search path
ENV PYTHONPATH=/app

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["pytest", "tests/test_RegexFileSearch.py"]