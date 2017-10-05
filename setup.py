from setuptools import setup

setup(
    name='mantid_pr_bot',
    version='0.1.0',
    py_modules=['mantid_pr_bot'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        mantid_pr_bot=mantid_pr_bot.main:main
    '''
)
