import sys

# Placeholder for a real 4B model loader (e.g. using llama_cpp)
def load_model():
    print("Loading 4B Parameter Model... (Simulation)")
    # import llama_cpp
    # return llama_cpp.Llama(model_path="path/to/model.gguf")
    return "Model Loaded"

def generate_response(prompt):
    # In reality: return model.create_completion(prompt)
    return "This is a simulated response from the Local AI (4B) for: " + prompt

if __name__ == "__main__":
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
        print(f"User: {prompt}")
        response = generate_response(prompt)
        print(f"AI: {response}")
    else:
        print("Usage: python simple_chat.py 'prompt'")
