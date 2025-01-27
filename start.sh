#!/usr/bin/env bash

# Activate the virtual environment
source /repo/docusign-hackathon-2024/bin/activate

# Set the environment variable
export PYTHONPATH="."

# Install the required libraries
pip install -r requirements.txt

# Run the Streamlit app
python -m streamlit run rental_agreement_agent.py

# Pause the script (optional)
read -p "Press Enter to exit..."
