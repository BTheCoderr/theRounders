from setuptools import setup, find_packages

setup(
    name="sports_betting",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit==1.29.0",
        "pandas<2.0.0,>=1.0.0",
        "numpy>=1.23.5",
        "scikit-learn>=1.0.0",
        "plotly>=5.18.0",
        "loguru>=0.7.2",
        "aiohttp>=3.8.0",
        "ray[default]>=2.7.0",
        "nfl_data_py==0.3.3",
        "pybaseball>=2.2.5"
    ]
) 