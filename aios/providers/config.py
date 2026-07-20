import os

CONFIG = {

    "groq":

        os.getenv("GROQ_API_KEY")
        or os.getenv("GROQ_API_KEY_1"),

    "cerebras":

        os.getenv("CEREBRAS_API_KEY"),

    "openrouter":

        os.getenv("OPENROUTER_API_KEY"),

    "anthropic":

        os.getenv("ANTHROPIC_API_KEY")

}
