# ☁️ Cloud-Scale LLM Evaluation Pipeline

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![AWS](https://img.shields.io/badge/AWS-Lambda%20%7C%20S3%20%7C%20DynamoDB-orange)
![Bedrock](https://img.shields.io/badge/Amazon-Bedrock-purple)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)

An event-driven, cloud-native LLM evaluation pipeline built on AWS.
Upload a prompt/response pair to S3 — Claude automatically evaluates
it via Bedrock and saves scores to DynamoDB for live dashboard monitoring.

> Third portfolio project for LLM QA / AI Ops / MLOps roles.

---

## 🏗️ Architecture
| Component | AWS Service | Purpose |
|---|---|---|
| File ingestion | Amazon S3 | Receives prompt/response JSON files |
| Orchestration | AWS Lambda | Auto-triggered evaluator engine |
| LLM Judge | Amazon Bedrock (Claude 3 Haiku) | Scores responses on 5 metrics |
| Storage | Amazon DynamoDB | Persists all evaluation results |
| Dashboard | Streamlit (local) | Visualises trends and scores |

---

## ✨ Features

- **Fully event-driven** — zero manual steps after upload
- **LLM-as-a-Judge** — Claude scores accuracy, relevance, completeness, clarity, hallucination
- **Auto-scaling** — Lambda handles any volume serverlessly
- **Live dashboard** — real-time trends, heatmaps, grade distribution
- **Cost-efficient** — runs almost entirely on AWS free tier (~$0.50 per 50 evals)

---

## 🚀 Setup Guide

### Prerequisites
- AWS account with free tier
- AWS CLI configured (`aws configure`)
- Python 3.11+
- Amazon Bedrock access enabled for Claude 3 Haiku in ap-south-1

### 1. Clone the repo

```bash
git clone https://github.com/shailesh9975/llm-eval-aws-pipeline
cd llm-eval-aws-pipeline
```

### 2. Deploy Lambda function

```bash
cd lambda
zip evaluator.zip evaluator.py

aws lambda create-function \
  --function-name llm-eval-function \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/llm-eval-lambda-role \
  --handler evaluator.lambda_handler \
  --zip-file fileb://evaluator.zip \
  --timeout 60 \
  --memory-size 256 \
  --region ap-south-1
```

### 3. Run the dashboard

```bash
pip install -r requirements.txt
cd dashboard
streamlit run app.py
```

### 4. Trigger an evaluation

```bash
aws s3 cp your_eval.json \
  s3://YOUR_BUCKET_NAME/inputs/your_eval.json
```

---

## 📁 Input File Format

```json
{
  "prompt": "What is machine learning?",
  "response": "The model response to evaluate",
  "reference": "The ideal ground truth answer"
}
```

---

## 📊 Evaluation Metrics

| Metric | Weight | Description |
|---|---|---|
| Accuracy | 30% | Factual correctness vs reference |
| Relevance | 25% | Does it answer the question? |
| Completeness | 20% | Covers key points? |
| Clarity | 15% | Clear and readable? |
| Hallucination | 10% | Penalises invented facts |

**Grade thresholds:** A ≥ 0.85 · B ≥ 0.75 · C ≥ 0.60 · F < 0.60

---

## 💰 Cost Estimate

| Service | Free Tier | Estimated Cost |
|---|---|---|
| S3 | 5GB free | $0.00 |
| Lambda | 1M requests free | $0.00 |
| DynamoDB | 25GB free | $0.00 |
| Bedrock (Claude Haiku) | Not free | ~$0.50 per 50 evals |

---

## 🗂️ Project Structure llm-eval-aws-pipeline/
│
├── lambda/
│   └── evaluator.py          # Lambda handler + Bedrock judge
│
├── dashboard/
│   └── app.py                # Streamlit dashboard
│
├── docs/
│   └── architecture.md       # Pipeline architecture
│
├── requirements.txt
└── README.md

cat > README.md << 'EOF'
# ☁️ Cloud-Scale LLM Evaluation Pipeline

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![AWS](https://img.shields.io/badge/AWS-Lambda%20%7C%20S3%20%7C%20DynamoDB-orange)
![Bedrock](https://img.shields.io/badge/Amazon-Bedrock-purple)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)

An event-driven, cloud-native LLM evaluation pipeline built on AWS.
Upload a prompt/response pair to S3 — Claude automatically evaluates
it via Bedrock and saves scores to DynamoDB for live dashboard monitoring.

> Third portfolio project for LLM QA / AI Ops / MLOps roles.

---

## 🏗️ Architecture
| Component | AWS Service | Purpose |
|---|---|---|
| File ingestion | Amazon S3 | Receives prompt/response JSON files |
| Orchestration | AWS Lambda | Auto-triggered evaluator engine |
| LLM Judge | Amazon Bedrock (Claude 3 Haiku) | Scores responses on 5 metrics |
| Storage | Amazon DynamoDB | Persists all evaluation results |
| Dashboard | Streamlit (local) | Visualises trends and scores |

---

## ✨ Features

- **Fully event-driven** — zero manual steps after upload
- **LLM-as-a-Judge** — Claude scores accuracy, relevance, completeness, clarity, hallucination
- **Auto-scaling** — Lambda handles any volume serverlessly
- **Live dashboard** — real-time trends, heatmaps, grade distribution
- **Cost-efficient** — runs almost entirely on AWS free tier (~$0.50 per 50 evals)

---

## 🚀 Setup Guide

### Prerequisites
- AWS account with free tier
- AWS CLI configured (`aws configure`)
- Python 3.11+
- Amazon Bedrock access enabled for Claude 3 Haiku in ap-south-1

### 1. Clone the repo

```bash
git clone https://github.com/shailesh9975/llm-eval-aws-pipeline
cd llm-eval-aws-pipeline
```

### 2. Deploy Lambda function

```bash
cd lambda
zip evaluator.zip evaluator.py

aws lambda create-function \
  --function-name llm-eval-function \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/llm-eval-lambda-role \
  --handler evaluator.lambda_handler \
  --zip-file fileb://evaluator.zip \
  --timeout 60 \
  --memory-size 256 \
  --region ap-south-1
```

### 3. Run the dashboard

```bash
pip install -r requirements.txt
cd dashboard
streamlit run app.py
```

### 4. Trigger an evaluation

```bash
aws s3 cp your_eval.json \
  s3://YOUR_BUCKET_NAME/inputs/your_eval.json
```

---

## 📁 Input File Format

```json
{
  "prompt": "What is machine learning?",
  "response": "The model response to evaluate",
  "reference": "The ideal ground truth answer"
}
```

---

## 📊 Evaluation Metrics
<img width="1907" height="987" alt="image" src="https://github.com/user-attachments/assets/85138aeb-559f-40e8-a591-6c1e9c3b06bb" />
<img width="1905" height="984" alt="image" src="https://github.com/user-attachments/assets/9699049a-ce53-450d-8061-a4a7911f1e1f" />
<img width="1904" height="983" alt="image" src="https://github.com/user-attachments/assets/71ee3bbb-d682-49cb-a757-246cd2ffdc08" />
<img width="1895" height="899" alt="image" src="https://github.com/user-attachments/assets/e5221227-e6cf-4fd1-8d37-9d548628e94a" />
<img width="1894" height="904" alt="image" src="https://github.com/user-attachments/assets/f4f45ffb-0dd3-496e-b9ba-b895942e9966" />


| Metric | Weight | Description |
|---|---|---|
| Accuracy | 30% | Factual correctness vs reference |
| Relevance | 25% | Does it answer the question? |
| Completeness | 20% | Covers key points? |
| Clarity | 15% | Clear and readable? |
| Hallucination | 10% | Penalises invented facts |

**Grade thresholds:** A ≥ 0.85 · B ≥ 0.75 · C ≥ 0.60 · F < 0.60

---

## 💰 Cost Estimate

| Service | Free Tier | Estimated Cost |
|---|---|---|
| S3 | 5GB free | $0.00 |
| Lambda | 1M requests free | $0.00 |
| DynamoDB | 25GB free | $0.00 |
| Bedrock (Claude Haiku) | Not free | ~$0.50 per 50 evals |

---

## 🗂️ Project Structure llm-eval-aws-pipeline/
│
├── lambda/
│   └── evaluator.py          # Lambda handler + Bedrock judge
│
├── dashboard/
│   └── app.py                # Streamlit dashboard
│
├── docs/
│   └── architecture.md       # Pipeline architecture
│
├── requirements.txt
└── README.md

---

## 🛠️ Tech Stack

Python · AWS Lambda · Amazon S3 · Amazon DynamoDB · Amazon Bedrock · Streamlit · Plotly · Boto3

---

## 📬 Contact

**Shailesh** · [LinkedIn](https://linkedin.com/in/YOUR_LINKEDIN) · [GitHub](https://github.com/shailesh9975)
