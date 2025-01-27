@ECHO OFF
REM Activate the virtual environment
CALL Scripts\activate.bat

REM Set the environment variables
SET "PYTHONPATH=."

REM Import the required libraries
pip install -r requirements.txt

REM Run the Streamlit app
python -m streamlit run rental_agreement_agent.py

REM Pause the script to see output/errors (optional)
PAUSE