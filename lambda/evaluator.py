# lambda/evaluator.py
# Triggered by S3 upload → evaluates prompt/response → saves to DynamoDB

import json
import uuid
import boto3
import re
from datetime import datetime, timezone

# ── AWS Clients ───────────────────────────────────────────────────────────────

s3       = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
bedrock  = boto3.client("bedrock-runtime", region_name="ap-south-1")

TABLE_NAME = "llm-eval-results"
MODEL_ID   = "anthropic.claude-3-haiku-20240307-v1:0"

# ── LLM-as-a-Judge Prompt ─────────────────────────────────────────────────────

JUDGE_PROMPT = """You are an expert LLM evaluator. Evaluate the following response against the reference answer.

PROMPT:
{prompt}

RESPONSE TO EVALUATE:
{response}

REFERENCE ANSWER:
{reference}

Score the response on each dimension from 0.0 to 1.0:

1. accuracy       - factual correctness compared to reference
2. relevance      - does it answer the actual question?
3. completeness   - does it cover the key points?
4. clarity        - is it clear and easy to understand?
5. hallucination  - 1.0 means no hallucination, 0.0 means severe hallucination

Respond ONLY in this exact JSON format, no other text:
{{
  "accuracy": 0.0,
  "relevance": 0.0,
  "completeness": 0.0,
  "clarity": 0.0,
  "hallucination": 0.0,
  "reasoning": "one sentence explanation"
}}"""

# ── Call Bedrock ──────────────────────────────────────────────────────────────

def call_bedrock_judge(prompt: str, response: str, reference: str) -> dict:
    """Send evaluation request to Claude via Bedrock."""

    judge_input = JUDGE_PROMPT.format(
        prompt=prompt,
        response=response,
        reference=reference,
    )

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "messages": [
            {"role": "user", "content": judge_input}
        ],
    })

    resp = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=body,
        contentType="application/json",
        accept="application/json",
    )

    result_body = json.loads(resp["body"].read())
    text = result_body["content"][0]["text"].strip()

    # Strip any markdown fences if present
    text = re.sub(r"```json|```", "", text).strip()

    scores = json.loads(text)
    return scores

# ── Compute Final Score ───────────────────────────────────────────────────────

def compute_final_score(scores: dict) -> float:
    weights = {
        "accuracy":      0.30,
        "relevance":     0.25,
        "completeness":  0.20,
        "clarity":       0.15,
        "hallucination": 0.10,
    }
    return round(sum(
        scores.get(k, 0) * w for k, w in weights.items()
    ), 3)

def grade(score: float) -> str:
    if score >= 0.85:   return "A"
    elif score >= 0.75: return "B"
    elif score >= 0.60: return "C"
    else:               return "F"

# ── Save to DynamoDB ──────────────────────────────────────────────────────────

def save_to_dynamodb(record: dict):
    table = dynamodb.Table(TABLE_NAME)
    table.put_item(Item=record)

# ── Lambda Handler ────────────────────────────────────────────────────────────

def lambda_handler(event, context):
    """
    Triggered by S3 PutObject event.
    Reads the uploaded JSON file, evaluates it, saves result to DynamoDB.
    """

    # Extract bucket and key from S3 event
    record   = event["Records"][0]
    bucket   = record["s3"]["bucket"]["name"]
    key      = record["s3"]["object"]["key"]

    print(f"Processing: s3://{bucket}/{key}")

    # Read the uploaded file
    obj      = s3.get_object(Bucket=bucket, Key=key)
    payload  = json.loads(obj["body"].read().decode("utf-8"))

    prompt    = payload["prompt"]
    response  = payload["response"]
    reference = payload["reference"]

    # Call Claude as judge
    scores = call_bedrock_judge(prompt, response, reference)

    # Compute final score
    final  = compute_final_score(scores)

    # Build result record
    eval_record = {
        "eval_id":       str(uuid.uuid4()),
        "timestamp":     datetime.now(timezone.utc).isoformat(),
        "s3_key":        key,
        "prompt":        prompt,
        "response":      response,
        "reference":     reference,
        "accuracy":      str(round(scores.get("accuracy", 0), 3)),
        "relevance":     str(round(scores.get("relevance", 0), 3)),
        "completeness":  str(round(scores.get("completeness", 0), 3)),
        "clarity":       str(round(scores.get("clarity", 0), 3)),
        "hallucination": str(round(scores.get("hallucination", 0), 3)),
        "final_score":   str(final),
        "grade":         grade(final),
        "reasoning":     scores.get("reasoning", ""),
    }

    # Save to DynamoDB
    save_to_dynamodb(eval_record)

    print(f"Saved eval_id: {eval_record['eval_id']} | Score: {final} | Grade: {grade(final)}")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "eval_id":     eval_record["eval_id"],
            "final_score": final,
            "grade":       grade(final),
        })
    }
