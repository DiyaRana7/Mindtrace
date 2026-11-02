"""Python-powered personality assessment. Start with: python app.py"""

from __future__ import annotations

import html
import random
from datetime import date

from flask import Flask, abort, jsonify, make_response, render_template, request

app = Flask(__name__, template_folder="templates", static_folder="static")

# Illustrative, self-reflection scoring dimensions; these questions are not a
# validated personality test. Each answer contributes to several dimensions.
TRAITS = [
    {"key": "ambition", "name": "Ambition & drive", "color": "#9770cf", "low": "Purposeful & considered", "high": "Highly driven", "strength": "You seem drawn to growth, meaningful challenge, and asking what might be possible.", "balance": "You may prioritize meaning and personal fit over achievement for its own sake."},
    {"key": "connection", "name": "Connection & care", "color": "#df8a67", "low": "Self-directed", "high": "People-centered", "strength": "The people you trust and care about appear to play a meaningful role in your choices.", "balance": "You seem to leave room for your own boundaries and point of view in relationships."},
    {"key": "authenticity", "name": "Authenticity & independence", "color": "#62a484", "low": "Flexible with expectations", "high": "Strongly self-directed", "strength": "Being true to your own values and making room for your individuality seem important to you.", "balance": "You may value finding your own way while also drawing on trusted expectations and relationships."},
    {"key": "curiosity", "name": "Curiosity & exploration", "color": "#598faf", "low": "Reflective & deliberate", "high": "Curious & exploratory", "strength": "You seem willing to explore unfamiliar possibilities and examine different perspectives.", "balance": "You appear to appreciate reflection and a sense of direction alongside discovery."},
    {"key": "resilience", "name": "Resilience & adaptability", "color": "#d1aa48", "low": "Reflective & measured", "high": "Adaptable & persistent", "strength": "Your answers suggest you can consider a challenge from more than one angle and find a way forward.", "balance": "You may treat rest, reassessment, and knowing when to change course as parts of your resilience."},
]


def q(text, answers, scores):
    return {"text": text, "answers": answers, "scores": scores}


QUESTIONS = [
    q("At the end of your life, which realization would hurt you the most?", ["I had the ability to achieve great things but never tried.", "I achieved everything but lost the people who mattered.", "I spent my entire life trying to become someone I wasn't.", "I was so afraid of losing things that I never truly lived."], [{"ambition": 3, "resilience": 1}, {"ambition": 1, "connection": 3}, {"authenticity": 3, "connection": 1}, {"curiosity": 2, "resilience": 2}]),
    q("You receive a message revealing the exact date and circumstances of your death. Nobody else can ever know. What would you do?", ["Read it immediately.", "Delete it without opening it.", "Read only the date.", "Keep it hidden and open it when life becomes difficult."], [{"curiosity": 3, "resilience": 2}, {"resilience": 3, "authenticity": 1}, {"curiosity": 2, "resilience": 1}, {"resilience": 2, "curiosity": 1}]),
    q("For 24 hours, everyone around you can hear your actual thoughts. What would you do?", ["Avoid everyone until it disappears.", "Act normally. I have nothing to hide.", "Stay only with people I trust.", "Use this opportunity to express things I've never said."], [{"authenticity": 1, "resilience": 2}, {"authenticity": 3, "connection": 1}, {"connection": 2, "authenticity": 1}, {"authenticity": 2, "ambition": 1, "connection": 1}]),
    q("Someone offers you $500,000, but in exchange, your family gets access to your complete digital history — private chats, search history, social media and everything else. Would you accept?", ["Absolutely! I have nothing to hide.", "Never. My privacy is more valuable than money.", "It depends on what exactly they might discover.", "I'd accept only if they promise not to judge me."], [{"resilience": 2, "connection": 2}, {"authenticity": 3, "resilience": 1}, {"resilience": 2, "curiosity": 1}, {"connection": 2, "authenticity": 1}]),
    q("Someone you deeply trusted betrays you. Months later, they genuinely apologize. What would you do?", ["Forgive them, but things will never be the same.", "Give them another chance if their apology feels genuine.", "Walk away permanently. Some things cannot be repaired.", "Act normally, but watch whether their actions change."], [{"connection": 2, "resilience": 2}, {"connection": 3, "resilience": 2}, {"authenticity": 2, "resilience": 2}, {"curiosity": 1, "resilience": 3, "connection": 1}]),
    q("You meet another version of yourself. They have everything you've ever wanted but made completely different choices. What would you do?", ["Ask them what decisions led to their success.", "Feel jealous because they got the life I wanted.", "Wonder whether they are actually happy.", "Challenge them to prove their life is better than mine."], [{"curiosity": 2, "ambition": 2}, {"ambition": 2, "resilience": 1}, {"curiosity": 2, "authenticity": 2}, {"ambition": 2, "resilience": 2}]),
    q("You have one almost impossible goal. You're exhausted, nobody supports you, and quitting is the easiest option. What would you do?", ["Push through. My limits shouldn't decide my future.", "Take a break and return stronger.", "Question whether the goal is worth the struggle.", "Find another way. Giving up isn't the only option."], [{"ambition": 3, "resilience": 3}, {"resilience": 3, "authenticity": 1}, {"authenticity": 2, "curiosity": 2}, {"resilience": 3, "curiosity": 2, "ambition": 1}]),
    q("You work extremely hard for something, but someone else achieves it effortlessly. What would you genuinely feel?", ["Inspired. If they can do it, I can too.", "Jealous, but I'll never admit it.", "Disappointed in myself and question my abilities.", "Accept that everyone's journey and timing are different."], [{"ambition": 3, "resilience": 2}, {"ambition": 2, "authenticity": 1}, {"ambition": 1, "resilience": 1}, {"resilience": 3, "authenticity": 1}]),
    q("You get an entire year without financial responsibilities, academic pressure or expectations from anyone. What would you do?", ["Build something extraordinary and chase my dreams.", "Travel, explore and experience everything I've missed.", "Spend time with myself and understand who I really am.", "Spend time with loved ones and enjoy a peaceful life."], [{"ambition": 3, "resilience": 2}, {"curiosity": 3, "authenticity": 1}, {"authenticity": 3, "curiosity": 1}, {"connection": 3, "resilience": 1}]),
    q("Imagine nobody could ever criticize you, laugh at you or judge your decisions. What would you genuinely do?", ["Chase an ambitious dream I've always been afraid to pursue.", "Express my real personality without pretending.", "Take a completely different path from what everyone expects.", "Leave everything behind for a while and start life on my own terms."], [{"ambition": 3, "resilience": 2}, {"authenticity": 3, "connection": 1}, {"authenticity": 3, "curiosity": 2}, {"authenticity": 2, "curiosity": 2, "resilience": 1}]),
]

CHALLENGES = [
    {"text": "Ego 🦚 or Kindness 💙?", "answers": ["Ego 🦚", "Kindness 💙"], "scores": [{"ambition": 5, "connection": 1, "authenticity": 3, "curiosity": 2, "resilience": 3}, {"ambition": 2, "connection": 5, "authenticity": 4, "curiosity": 2, "resilience": 4}]},
    {"text": "Mountains 🏔️ or Beaches 🌊?", "answers": ["Mountains 🏔️", "Beaches 🌊"], "scores": [{"curiosity": 5, "authenticity": 4, "resilience": 4, "ambition": 4, "connection": 2}, {"curiosity": 4, "authenticity": 4, "resilience": 2, "ambition": 2, "connection": 5}]},
    {"text": "Sunrise 🌅 or Midnight 🌙?", "answers": ["Sunrise 🌅", "Midnight 🌙"], "scores": [{"ambition": 5, "resilience": 5, "connection": 3, "authenticity": 3, "curiosity": 3}, {"ambition": 3, "resilience": 3, "connection": 3, "authenticity": 5, "curiosity": 5}]},
    {"text": "Rain 🌧️ or Snow ❄️?", "answers": ["Rain 🌧️", "Snow ❄️"], "scores": [{"curiosity": 3, "authenticity": 4, "connection": 3, "resilience": 4, "ambition": 3}, {"curiosity": 5, "authenticity": 4, "connection": 3, "resilience": 4, "ambition": 3}]},
    {"text": "Fame ⭐ or Freedom 🕊️?", "answers": ["Fame ⭐", "Freedom 🕊️"], "scores": [{"ambition": 5, "connection": 3, "authenticity": 2, "curiosity": 3, "resilience": 4}, {"ambition": 3, "connection": 3, "authenticity": 5, "curiosity": 5, "resilience": 4}]},
    {"text": "Past 🔙 or Future 🔮?", "answers": ["Past 🔙", "Future 🔮"], "scores": [{"ambition": 2, "connection": 4, "authenticity": 4, "curiosity": 3, "resilience": 3}, {"ambition": 5, "connection": 2, "authenticity": 3, "curiosity": 5, "resilience": 4}]},
    {"text": "Deep Conversations 🌌 or Silly Conversations 😂?", "answers": ["Deep Conversations 🌌", "Silly Conversations 😂"], "scores": [{"ambition": 3, "connection": 5, "authenticity": 5, "curiosity": 4, "resilience": 3}, {"ambition": 2, "connection": 4, "authenticity": 3, "curiosity": 3, "resilience": 4}]},
    {"text": "Being Understood or Being Admired?", "answers": ["Being Understood", "Being Admired"], "scores": [{"ambition": 2, "connection": 5, "authenticity": 5, "curiosity": 3, "resilience": 3}, {"ambition": 5, "connection": 2, "authenticity": 3, "curiosity": 3, "resilience": 4}]},
    {"text": "One True Friend or A Thousand Acquaintances?", "answers": ["One True Friend", "A Thousand Acquaintances"], "scores": [{"ambition": 2, "connection": 5, "authenticity": 4, "curiosity": 3, "resilience": 3}, {"ambition": 4, "connection": 2, "authenticity": 3, "curiosity": 5, "resilience": 4}]},
    {"text": "Restart Your Life or See Your Future?", "answers": ["Restart Your Life", "See Your Future"], "scores": [{"ambition": 4, "connection": 3, "authenticity": 5, "curiosity": 4, "resilience": 2}, {"ambition": 3, "connection": 3, "authenticity": 2, "curiosity": 4, "resilience": 5}]},
]

HOBBIES = {
    "ambition": [("Choose one meaningful goal", "Pick something important to you and break it into an easy first step."), ("Try a personal project", "Make something or learn something without needing to prove anything.")],
    "connection": [("Plan an unhurried catch-up", "Make time for a conversation with someone you trust."), ("Try a shared-table activity", "Cook, create, or walk with someone whose company you enjoy.")],
    "authenticity": [("Keep a values journal", "Write about the moments when you feel most like yourself."), ("Explore a just-for-you hobby", "Try something because it interests you, without measuring the outcome.")],
    "curiosity": [("Follow a new question", "Choose a topic you know little about and explore it for fun."), ("Visit somewhere unfamiliar", "Take a low-pressure day trip and see what catches your attention.")],
    "resilience": [("Build a gentle reset ritual", "Find a small routine that helps you regain perspective."), ("Try a beginner-friendly class", "Explore something new and let yourself learn at your own pace.")],
}


def analyze_answers(answers, challenge_answers):
    if not isinstance(answers, list) or len(answers) != len(QUESTIONS) or any(type(answer) is not int or answer not in range(4) for answer in answers):
        abort(400, "Please answer all 10 personality questions to reveal your report.")
    if not isinstance(challenge_answers, list) or len(challenge_answers) != len(CHALLENGES) or any(type(answer) is not int or answer not in range(2) for answer in challenge_answers):
        abort(400, "Please complete all 10 First Instinct Challenge choices to reveal your report.")
    totals = {trait["key"]: 0 for trait in TRAITS}
    for question, selected in zip(QUESTIONS, answers):
        for key, points in question["scores"][selected].items():
            totals[key] += points
    # Normalize each dimension to 0–100 for a visual, relative reflection scale.
    challenge_totals = {trait["key"]: 0 for trait in TRAITS}
    for question, selected in zip(CHALLENGES, challenge_answers):
        for key in challenge_totals:
            challenge_totals[key] += question["scores"][selected][key]
    maxima = {trait["key"]: sum(max(option.get(trait["key"], 0) for option in question["scores"]) for question in QUESTIONS) for trait in TRAITS}
    primary = {key: round(totals[key] / maximum * 100) if maximum else 0 for key, maximum in maxima.items()}
    first_instinct = {key: round((amount / len(CHALLENGES) - 1) / 4 * 100) for key, amount in challenge_totals.items()}
    scores = {key: round(primary[key] * .7 + first_instinct[key] * .3) for key in totals}
    ranked = sorted(TRAITS, key=lambda trait: scores[trait["key"]], reverse=True)
    lead = ranked[0]
    second = ranked[1]
    profiles = {
        "ambition": ("The Purposeful Achiever", "Big intentions, grounded in a real desire to grow.", "You seem motivated by possibility and the chance to put effort toward something meaningful. Your answers suggest an appetite for challenge, along with an opportunity to reflect on what success means to you."),
        "connection": ("The Deeply Connected One", "Relationships have a special place in your story.", "Your answers suggest that trust, closeness, and shared experiences carry real weight for you. You seem to consider the people involved as you make choices and imagine what matters most."),
        "authenticity": ("The True-to-Yourself Explorer", "Your own values matter more than other people's scripts.", "Your answers suggest a strong interest in being honest with yourself and making choices that feel genuinely your own. You seem to value having room to discover what fits you."),
        "curiosity": ("The Open-Hearted Explorer", "A new perspective can open an entirely new door.", "Your answers suggest curiosity about what might be possible, different choices, and the questions that sit underneath everyday life. Exploring a new perspective appears to appeal to you."),
        "resilience": ("The Thoughtful Wayfinder", "You give yourself room to reflect and find your next step.", "Your answers suggest that you can weigh a situation before choosing how to respond. Reflection, adjusting course, and thinking about the long view may all be part of how you move forward."),
    }
    title, tagline, description = profiles[lead["key"]]
    insights = [
        {"title": f"A strength to notice: {lead['name'].lower()}", "copy": lead["strength"]},
        {"title": f"Another side of you: {second['name'].lower()}", "copy": second["strength"] if scores[second["key"]] >= 50 else second["balance"]},
        {"title": "A useful thing to remember", "copy": "Your answers describe how you see yourself today. Different situations can bring out different sides of you."},
    ]
    ideas = [{"title": title, "copy": copy} for trait in ranked[:3] for title, copy in HOBBIES[trait["key"]]][:4]
    return {"profile": {"name": title, "tagline": tagline, "description": description}, "scores": scores, "traits": [{**trait, "score": scores[trait["key"]]} for trait in TRAITS], "insights": insights, "hobbies": ideas, "reflection": f"What could it look like to make a little more room for {lead['name'].lower()} in your everyday life?", "assessmentComplete": True}


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/quiz")
def quiz():
    return jsonify({"questions": [{"category": f"QUESTION {index + 1:02d}", "text": item["text"], "answers": item["answers"]} for index, item in enumerate(QUESTIONS)]})


@app.get("/api/challenge")
def first_instinct_challenge():
    return jsonify({"questions": [{"text": question["text"], "answers": question["answers"]} for question in CHALLENGES]})


@app.post("/api/analyze")
def analyze():
    payload = request.get_json(silent=True) or {}
    return jsonify(analyze_answers(payload.get("answers"), payload.get("challengeAnswers")))


@app.post("/api/report")
def report():
    payload = request.get_json(silent=True) or {}
    result = analyze_answers(payload.get("answers"), payload.get("challengeAnswers"))
    safe = lambda value: html.escape(str(value), quote=True)
    parts = ["<!doctype html><html lang='en'><meta charset='utf-8'><meta name='viewport' content='width=device-width'><title>Your Personality Detective report</title><style>body{max-width:760px;margin:40px auto;padding:24px;background:#f8f6f1;color:#322b38;font:16px/1.7 system-ui}h1{font-size:42px;color:#7454ab}.card{padding:20px;margin:18px 0;background:white;border:1px solid #e9e3ee;border-radius:14px}.bar{height:11px;background:#eee9f1;border-radius:9px}.fill{height:100%;border-radius:9px}.small{color:#756e78;font-size:13px}@media print{.card{break-inside:avoid}}</style><body>", f"<p>PERSONALITY DETECTIVE · YOUR PRIVATE REFLECTION · {date.today().strftime('%B %d, %Y')}</p><h1>{safe(result['profile']['name'])}</h1><p>{safe(result['profile']['tagline'])}</p><p>{safe(result['profile']['description'])}</p><section class='card'><h2>Your personality patterns</h2>"]
    for trait in result["traits"]:
        parts.append(f"<p><strong>{safe(trait['name'])}</strong> · {trait['score']}%</p><div class='bar'><div class='fill' style='width:{trait['score']}%;background:{safe(trait['color'])}'></div></div>")
    parts.append("</section><section class='card'><h2>A closer look</h2>")
    for insight in result["insights"]:
        parts.append(f"<p><strong>{safe(insight['title'])}</strong><br>{safe(insight['copy'])}</p>")
    parts.append("</section><section class='card'><h2>A few things to try</h2>")
    for idea in result["hobbies"]:
        parts.append(f"<p><strong>{safe(idea['title'])}</strong><br>{safe(idea['copy'])}</p>")
    parts.append(f"</section><section class='card'><h2>A question to keep</h2><p>{safe(result['reflection'])}</p></section><p class='small'>For self-reflection; this short questionnaire is not a clinical diagnosis or scientifically validated personality test.</p></body></html>")
    response = make_response("".join(parts))
    response.headers["Content-Disposition"] = "attachment; filename=personality-detective-report.html"
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.after_request
def privacy_headers(response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
