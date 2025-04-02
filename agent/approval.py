from utils.logger import logger


def approval_flow(subject, response):
    print("\nSuggested Response:")
    print("-" * 60)
    print(response)
    print("-" * 60)
    
    while True:
        user_input = input("Action? [A]pprove / [E]dit / [S]kip: ").strip().lower()
        if user_input == 'a':
            logger.info(f"✅ Approved response for: {subject}")
            return response  # future: send via Gmail API
        elif user_input == 'e':
            print("\nEnter your edited response (end with a blank line):")
            edited_lines = []
            while True:
                line = input()
                if not line:
                    break
                edited_lines.append(line)
            edited_response = "\n".join(edited_lines)
            logger.info(f"✏️ Edited response for: {subject}")
            return edited_response
        elif user_input == 's':
            logger.info(f"⏭️ Skipped responding to: {subject}")
            return None
        else:
            print("Invalid input. Please enter A, E, or S.")
    