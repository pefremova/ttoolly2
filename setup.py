from setuptools import setup

setup(
    name="ttoolly2",
    version="0.1",
    description="form test cases and utils",
    author="Polina Mishchenko",
    author_email="polina.v.mishchenko@gmail.com",
    packages=[
        "ttoolly",
    ],
    entry_points={
        "console_scripts": [
            "tt_get_field_template = ttoolly.commands.get_field_template:main",
            "tt_generate_cases = ttoolly.commands.generate_cases:main",
        ],
    },
    install_requires=["Faker>=19.6.1"],
)
