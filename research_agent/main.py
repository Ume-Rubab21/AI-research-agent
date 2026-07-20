import time

from agent.builder import build_agent
from memory.session_memory import SessionMemory


def main():

    agent = build_agent()

    memory = SessionMemory()

    print("=" * 50)
    print("        AI Research Agent")
    print("=" * 50)

    while True:

        question = input("\nYou : ")

        if question.lower() == "exit":
            print("\nGoodbye!")
            break

        memory.add_user_message(question)

        print("\n🤖 Thinking...\n")

        answer = get_answer_with_retry(agent, memory)

        print("🤖", answer)

        memory.add_ai_message(answer)


def get_answer_with_retry(agent, memory, max_retries=3):
    """
    Calls the agent, and if it fails (e.g. a malformed tool call
    from the model), retries silently a few times before giving
    the user a friendly fallback message.
    """

    last_error = None

    for attempt in range(max_retries):

        try:
            result = agent.invoke(
                {
                    "messages": memory.get_messages()
                }
            )
            return result["messages"][-1].content

        except Exception as e:
            last_error = e
            time.sleep(1)
            continue

    return (
        "I couldn't process that just now, could you try rephrasing "
        "your question?"
    )


if __name__ == "__main__":
    main()