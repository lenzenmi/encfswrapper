from distutils.core import setup

setup(
    name='encfswrapper',
    version='1.0.0',
    packages=['encfswrapper'],
    scripts=['scripts/encfswrapper'],

    # metadata for upload to PyPI
    author="Mike Lenzen",
    author_email="lenzenmi@example.com",
    description=('A program to mount an encfs filesystem while another program'
                   ' executes.'),
    license="GPL3",
    keywords="encfs",
    url="",  # project home page, if any
)
