from setuptools import setup, find_packages
setup(
    name = "encfswrapper",
    version = "1.0.0",
    packages = find_packages(),
    entry_points = {
        'console_scripts': [
            'encfswrapper = encfswrapper.encfswrapper:main',
        ]
    },

    # metadata for upload to PyPI
    author = "Mike Lenzen",
    author_email = "lenzenmi@example.com",
    description = "A program to mount an encfs filesystem while another program executes.",
    license = "GPL3",
    keywords = "encfs",
    url = "",   # project home page, if any
)
