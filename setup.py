from setuptools import setup

setup(
    name='mantid_pr_bot',
    version='0.1.0',
    author='Dan Nixon',
    author_email='daniel.nixon@stfc.ac.uk',
    py_modules=['mantid_pr_bot'],
    install_requires=[
        'Click',
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
