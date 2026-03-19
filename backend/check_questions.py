import json

data = json.load(open('/Users/shivc/Documents/Workspace/JS/qna-ai-admin/all-questions/consolidated_questions.json'))
print(f'Total items: {len(data)}')
print(f'First item keys: {list(data[0].keys()) if data else "empty"}')
print(f'First 3 questions:')
for i, item in enumerate(data[:3]):
    q = item.get("question", str(item)[:80])
    print(f'  {i+1}. {q}')