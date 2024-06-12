REM Author: Shumpei Sugita
REM Last Modified: 2024/05/29
REM Description: This batch file is used to set up the Python environment for the Compound Eye Simulator project.
REM Usage: Run this batch file in the root directory of the project.

REM pipenv installation

REM pip3 install pipenv
REM pipenv --python 3.11

REM pipenv setting
CALL pipenv shell 
CALL pipenv install 