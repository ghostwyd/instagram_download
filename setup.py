# coding:utf-8

from setuptools import setup, find_packages

setup(
        name='instagram_download',
        version='1.0.1',
        description='this tool is used to download posts from instagram',
        author='ghostwyd',
        author_email='muou1986227@163.com',
        url='https://github.com/ghostwyd/instagram_download',
        platforms = "any",
        python_requires='>=3.5',
        license='MIT',
        entry_points={'console_scripts': ['instagram_download=instagram_download.login_instagram:main']},
        py_modules = ['instagram_download.user', 'instagram_download.util'],
        packages=['instagram_download', 'instagram_download.user', 'instagram_download.util']
        )
