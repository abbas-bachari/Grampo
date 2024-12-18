from setuptools import setup, find_packages
requires=[r.strip() for r in open('requirements.txt','r',encoding='utf-8').readlines() if r.strip()]
# requires=[]

setup(
    name='Grampo',
    version='1.0.6',
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
    
    install_requires=requires ,
    
    keywords=[
        'telethon',
        'telegram',
        'telegram multi session', 
        'telegram-python', 
        'opentele',  
        'api', 
        'abbas bachari'],
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
       
    ],
)


