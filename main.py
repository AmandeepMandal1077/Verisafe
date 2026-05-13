from code_generation.llm_context_demo import generate_response

def main():
    print("Initializing test prompt...")
    prompt = "answer 2 + 2"
    
    print(f"Sending prompt using provider...")

    # context = generate_response(prompt, strategy="math_test", provider="ollama", model_name="gemma3:4b")
    context = generate_response(prompt, strategy="math_test", provider="google", model_name="gemini-2.5-flash")
    print(context);

if __name__ == "__main__":
    main()
