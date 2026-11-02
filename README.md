# Personality Detective

A simple, private personality reflection app with three parts: a 10-question deep personality assessment, a 10-choice First Instinct Challenge, and a personalized report based on both rounds.

## Run

With Python 3.9 or newer, run:

```powershell
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

The first round uses the ten situations and four answers supplied for this project. The second round uses ten quick either-or choices. Both rounds are required before the combined report is prepared. Answers are processed in memory and not saved. Results are prompts for reflection, not a validated psychological test or diagnosis.
