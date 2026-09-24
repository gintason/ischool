# your_app/grading/gpt_grader.py
import json
import logging
from django.conf import settings
from openai import OpenAI

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def grade_theory_answer(question_text, expected_answer, student_answer):
    if not student_answer or not student_answer.strip():
        return {"score": 0, "comment": "No answer provided."}

    prompt = f"""
Grade the following student's answer on a scale of 0 to 100 based on its accuracy, completeness, and relevance to the expected answer.

Question: {question_text}
Expected Answer: {expected_answer}
Student Answer: {student_answer}

Return a valid JSON object with key "score" (integer 0-100) and "comment" (string).
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Highly cost-effective and accurate for grading
            response_format={"type": "json_object"},  # Guarantees JSON output
            messages=[
                {"role": "system", "content": "You are a fair and precise educational grading assistant. Respond only in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        result_text = response.choices[0].message.content
        result = json.loads(result_text)
        
        # Ensure score is numeric
        score = result.get("score", 0)
        try:
            score = float(score)
        except (ValueError, TypeError):
            score = 0.0

        return {
            "score": min(max(score, 0), 100),
            "comment": result.get("comment", "")
        }
    except Exception as e:
        logger.error(f"GPT grading failed: {e}")
        return {"score": 0, "comment": "Auto-grading failed due to a system error."}
