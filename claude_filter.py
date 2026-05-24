# claude_filter.py
import anthropic, json

def filter_and_rank_jobs(jobs: list[dict], skillset: list[str]) -> list[dict]:
    client = anthropic.Anthropic()
    
    prompt = f"""
    My technical skillset: {', '.join(skillset)}
    
    Here are job postings from the last 12 hours:
    {json.dumps(jobs, indent=2)}
    
    Please:
    1. Filter out jobs that are NOT relevant to my skillset
    2. Rank remaining jobs by relevance (1 = best match)
    3. Add a "match_reason" field explaining why each is relevant
    4. Return ONLY a JSON array of matched jobs with a "rank" field added
    """
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    content = response.content[0].text
    # Strip markdown fences if present
    clean = content.replace("```json", "").replace("```", "").strip()
    return json.loads(clean)
