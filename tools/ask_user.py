# tool: {"name": "ask_user", "description": "向用户询问一个开放式问题，并等待用户输入答案"}
def ask_user(question: str) -> str:
    print(f"\n🤖 模型想问您: {question}")
    answer = input("👤 您的回答: ")
    return answer
