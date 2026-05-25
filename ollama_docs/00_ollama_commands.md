ollama serve          # Start the Ollama server (required before using models)


ollama list           # List all downloaded models
ollama pull <model>   # Download a model (e.g., ollama pull llama3)
ollama rm <model>     # Remove/delete a model
ollama show <model>   # Show model information and details

ollama run <model>    # Start interactive chat with a model (e.g., ollama run llama3)
ollama run <model> "prompt"  # Run with a single prompt and exit

ollama pull llama3.2        # Meta's Llama 3.2
ollama pull mistral         # Mistral 7B
ollama pull codellama       # Code-focused model
ollama pull gemma2          # Google's Gemma 2
ollama pull phi3            # Microsoft's Phi-3


ollama ps             # Show currently running models
ollama cp <src> <dst> # Copy a model
ollama create <name> -f Modelfile  # Create a custom model from a Modelfile