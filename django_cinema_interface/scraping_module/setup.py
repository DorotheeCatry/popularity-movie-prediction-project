from setuptools import setup, find_packages

setup(
    name='allocine_scraper',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'scrapy',
        'psycopg2-binary',
        'python-dotenv',
        'django',
        'selenium',
        'webdriver_manager',
    ],
    entry_points={
        'scrapy': ['settings = allocine_scraper.settings']
    }
)