# Add this to your plugin's __init__.py or main entry point file

def plugin_init():
    """Initialize the plugin components."""
    try:
        # Initialize LLM providers
        from llm.llm_service_provider import initialize_llm_providers
        initialize_llm_providers()
        Gimp.message("Initialized LLM providers")
    except Exception as e:
        Gimp.message(f"Error initializing LLM providers: {str(e)}")

# Call this function when your plugin loads