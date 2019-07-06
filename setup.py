import setuptools

setuptools.setup(
    name="flake8-gl-codeclimate",
    license="MIT",
    version="0.1.2",
    description="Gitlab Code Quality artifact Flake8 formatter.",
    author="Arne Welzel",
    author_email="arne.welzel@gmail.com",
    url="https://github.com/awelzel/flake8-gl-codeclimate",
    packages=[
        "flake8_gl_codeclimate",
    ],
    install_requires=[
        "flake8 > 3.0.0",
    ],
    scripts=[
        "scripts/report-to-codeclimate.py",
    ],
    entry_points={
        "flake8.report": [
            'gl-codeclimate = flake8_gl_codeclimate:GitlabCodeClimateFormatter',
        ],
    }
)
