# Pipeline Architecture

S3 (Upload) → Lambda (Evaluate) → Bedrock Claude (Judge) → DynamoDB (Store) → Streamlit (Visualise)

## Flow
1. User uploads JSON file to S3 inputs/ folder
2. S3 triggers Lambda automatically
3. Lambda reads the file and calls Claude via Bedrock
4. Claude scores the response on 5 metrics
5. Scores saved to DynamoDB
6. Streamlit dashboard reads DynamoDB and shows live results
