# your_app/grading/gpt_grader.py
import json
import logging
from django.conf import settings
from openai import OpenAI  # ✅ New import for client-based syntax

logger = logging.getLogger(__name__)

# ✅ Create OpenAI client with your API key
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def grade_theory_answer(question_text, expected_answer, student_answer):
    prompt = f"""
Grade the following student's answer on a scale of 0 to 100 based on its accuracy, completeness, and relevance to the expected answer.

Question: {question_text}
Expected Answer: {expected_answer}
Student Answer: {student_answer}

Return only a JSON object in the format: {{ "score": number, "comment": "your brief comment" }}.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a grading assistant that evaluates exam answers."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        result_text = response.choices[0].message.content
        result = json.loads(result_text)
        return result
    except Exception as e:
        logger.error(f"GPT grading failed: {e}")
        return {"score": 0, "comment": "Auto-grading failed."}
