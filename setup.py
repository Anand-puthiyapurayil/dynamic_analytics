from setuptools import setup, find_packages

setup(
    name="dynamic_analytics",
    version="1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "dash",
        "pandas",
        "plotly",
        "seaborn",
        "numpy",
        "dash-bootstrap-components",
    ],
)