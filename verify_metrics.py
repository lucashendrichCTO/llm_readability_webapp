from main import llm_readability_score

baseline_text = """
The concept of artificial intelligence has been around for decades, but recent advancements in large language models have transformed the landscape significantly. These models are capable of understanding and generating human-like text, which opens up new possibilities for automation and creativity. However, to make the most of these tools, one must understand how they process information. It is not just about feeding them data; it is about structuring that data in a way that aligns with their training patterns. This involves using clear sentences, avoiding ambiguity, and providing context where necessary. Many people fail to realize that the way they format their content can have a massive impact on how well an AI can understand and retrieve it.
This is the second paragraph. It continues to discuss the topic in a general way without using specific question headings or clear structures.
"""

optimized_text = """
Start with the answer.
Optimizing for LLMs requires structured data, question-based headings, and clear answers.

How do I optimize for AI?
Use an inverted pyramid structure. Place the most important information at the start of your content. This ensures that AI models, which prioritize the beginning of text, capture the core message immediately.

What is the benefit?
Question: Why use this format?
Answer: It aligns with how users query AI systems.
"""

print(f"Baseline Score: {llm_readability_score(baseline_text)}")
print(f"Optimized Score: {llm_readability_score(optimized_text)}")
