import json

data = json.load(open('/Users/shivc/Documents/Workspace/JS/qna-ai-admin/all-questions/consolidated_questions.json'))
questions = data.get('questions', [])
print(f'Total questions: {len(questions)}')
print(f'Type: {type(questions)}')

if isinstance(questions, list) and questions:
    print(f'First question keys: {list(questions[0].keys())}')
    print(f'First 3 questions:')
    for i, q in enumerate(questions[:3]):
        q_str = q.get("question", str(q))
        print(f'  {i+1}. {q_str[:80]}...' if len(q_str) > 80 else f'  {i+1}. {q_str}')
else:
    print("No questions found or not a list")