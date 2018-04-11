from setuptools import setup, find_packages


setup(
    name='mantid_pr_bot',
    version='0.1.0',
    author='Dan Nixon',
    author_email='daniel.nixon@stfc.ac.uk',
    py_modules=find_packages(),
    install_requires=[
        'Click>=5.0.0',
        'requests',
    ],
    entry_points='''
        [console_scripts]
        mantid_pr_bot=mantid_pr_bot.main:main
    ''',
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux'
    ]
)
