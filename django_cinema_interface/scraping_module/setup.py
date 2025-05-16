from setuptools import setup, find_packages

setup(
    name='scraping_module',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'scrapy>=2.12.0',
        'psycopg2-binary>=2.9.10',
        'python-dotenv>=1.1.0',
        'django>=5.2',
        'selenium>=4.31.0',
        'webdriver_manager>=4.0.2',
        'dateparser>=1.2.1',
        'fake-useragent>=2.1.0',
        'scrapy-user-agents>=0.1.1',
    ],
    python_requires='>=3.8',
)