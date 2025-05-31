# main.py

import os
from agent_orchestrator import AgentOrchestrator

def display_intro():
    print("\n=== AI Agent Orchestrator ===")
    print("Choose input format:")
    print("1. PDF")
    print("2. Email (paste text or provide file)")
    print("3. JSON (paste text or provide file)")
    print("4. Exit")

def get_input_text():
    choice = input("\nChoose input method:\n1. Paste text\n2. Provide file path\nEnter choice (1/2): ")
    if choice == '1':
        print("Paste your content below. End input with a blank line:")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        return "\n".join(lines)
    elif choice == '2':
        file_path = input("Enter file path: ").strip()
        if not os.path.isfile(file_path):
            print("[ERROR] File not found.")
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        print("[ERROR] Invalid choice.")
        return None

def main():
    orchestrator = AgentOrchestrator()
    sender = "test_user@example.com"
    conversation_id = "conv_test_001"

    while True:
        display_intro()
        choice = input("Enter your choice (1/2/3/4): ")

        if choice == '1':
            pdf_path = input("Enter full path to the PDF file: ").strip()
            if not os.path.isfile(pdf_path):
                print("[ERROR] PDF file not found.")
                continue
            with open(pdf_path, 'rb') as f:
                text = f.read()
            source_hint = text.decode('utf-8', errors='ignore') if len(text) < 100 else text.decode('utf-8', errors='ignore')[:100] + "..."
            result = orchestrator.route_input(text, sender=sender, conversation_id=conversation_id, input_format="PDF", source_hint=source_hint)
            print("\n=== PDF Processing Result ===")
            print(result)

        elif choice in ('2', '3'):
            input_data = get_input_text()
            if input_data:
                result = orchestrator.route_input(input_data, sender=sender, conversation_id=conversation_id)
                print("\n=== Processing Result ===")
                print(result)

        elif choice == '4':
            print("Exiting.")
            break

        else:
            print("[ERROR] Invalid option. Try again.")

if __name__ == "__main__":
    main()
