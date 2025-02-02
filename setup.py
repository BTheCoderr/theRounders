from setuptools import setup, find_packages

setup(
    name="nba_analytics",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'pandas>=2.2.3',
        'numpy<2,>=1.19.3',
        'nba_api>=1.4.1',
        'streamlit>=1.31.0',
        'plotly>=6.0.0',
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A sports betting analytics platform",
    keywords="sports betting, analytics, predictions",
    python_requires='>=3.9',
) 