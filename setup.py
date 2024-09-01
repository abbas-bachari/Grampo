from setuptools import setup, find_packages

setup(
    name='Grampo',
    version='1.0.0',
    author='Abbas Bachari',
    author_email='abbas-bachari@hotmail.com',
    description='A Python Telegram API Library , with official Telegram APIs.',
    long_description=open('README.md',encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    packages=find_packages(),
    url='https://github.com/abbas-bachari/Grampo',
    python_requires='>=3.10',
    project_urls={
    "Homepage":'https://github.com/abbas-bachari/Grampo',
    'Documentation': 'https://github.com/abbas-bachari/Grampo',
    'Source': 'https://github.com/abbas-bachari/Grampo/',
    'Tracker': 'https://github.com/abbas-bachari/Grampo/issues',
   
},
    
    install_requires=[
                    
                    'PyQt5',
                    'TgCrypto',
                    'telethon',
                    'psutil',
                    'python-socks[asyncio]',
                    'loguru'
                    ],
    
    keywords=[
        'telethon',
        'telegram',
        'telegram multi session', 
        'telegram-pythom', 
        'opentele',  
        'api', 
        'abbas bachari'],
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
        'Programming Language :: Python 3.11'
    ],
)


