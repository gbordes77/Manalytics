from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="manalytics",
    version="1.0.0",
    author="Guillaume",
    description="MTG Meta Analysis Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/manalytics",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "httpx>=0.25.0",
        "beautifulsoup4>=4.12.0",
        "pandas>=2.1.0",
        "fastapi>=0.108.0",
        "psycopg2-binary",
        "redis",
        "python-dotenv",
        "pydantic-settings",
        "unidecode",
        "selenium",
        "matplotlib",
        "seaborn",
        "click",
        "tqdm"
    ],
    entry_points={
        "console_scripts": [
            "manalytics=scripts.run_pipeline:main",
            "manalytics-api=src.api.app:main",
        ],
    },
    include_package_data=True,
)