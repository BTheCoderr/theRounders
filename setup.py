from setuptools import setup, find_packages

setup(
    name="sports_betting",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.29.0",
        "pandas>=1.0.0",
        "python-dotenv>=1.0.0",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A sports betting analytics platform",
    keywords="sports betting, analytics, predictions",
    python_requires=">=3.8",
) 