import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.content_filter_strategy import PruningContentFilter, BM25ContentFilter
from bs4 import BeautifulSoup
import openai
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    # 1. Crawl with minimal or no markdown generator, just get raw HTML
    config = CrawlerRunConfig(
        # If you only want raw HTML, you can skip passing a markdown_generator
        # or provide one but focus on .html in this example
    )

    async with AsyncWebCrawler() as crawler:
        links = {
            "https://ai.pydantic.dev/models/": "models",
            "https://ai.pydantic.dev/agents/": "agents",
            "https://ai.pydantic.dev/tools/": "tools",
            "https://ai.pydantic.dev/results/": "results",
            "https://ai.pydantic.dev/message-history/": "message-history",
            "https://ai.pydantic.dev/testing-evals/": "testing-evals",
            "https://ai.pydantic.dev/logfire/": "logfire",
            "https://ai.pydantic.dev/multi-agent-applications/": "multi-agent-applications",
            "https://ai.pydantic.dev/graph/": "graph",
            "https://ai.pydantic.dev/examples/chat-app/": "chat-app",
            "https://ai.pydantic.dev/examples/rag/": "rag",
            "https://ai.pydantic.dev/examples/sql-gen/": "sql-gen",

        }
        for link, filename in links.items():
            result = await crawler.arun(link, config=config)

            if not result.success or not result.html:
                print("Crawl failed or no HTML content.")
                return

            raw_html = result.html

            with open(f"docs/pydantic-ai/{filename}.html", "w") as f:
                f.write(raw_html)

            client = openai.Client()
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts the documentation and code examples from html and returns them in markdown format"},
                    {"role": "user", "content": raw_html}
                ],
            )

            with open(f"docs/pydantic-ai/{filename}.md", "w") as f:
                f.write(response.choices[0].message.content)

        # # 2. First pass: PruningContentFilter on raw HTML
        # pruning_filter = PruningContentFilter(threshold=0.5, min_word_threshold=1)

        # # filter_content returns a list of "text chunks" or cleaned HTML sections
        # pruned_chunks = pruning_filter.filter_content(raw_html)
        # # This list is basically pruned content blocks, presumably in HTML or text form

        # # For demonstration, let's combine these chunks back into a single HTML-like string
        # # or you could do further processing. It's up to your pipeline design.
        # pruned_html = "\n".join(pruned_chunks)

        # # 3. Second pass: BM25ContentFilter with a user query
        # bm25_filter = BM25ContentFilter(
        #     user_query="code examples",
        #     bm25_threshold=1.2,
        #     language="english"
        # )

        # # returns a list of text chunks
        # bm25_chunks = bm25_filter.filter_content(pruned_html)  

        # if not bm25_chunks:
        #     print("Nothing matched the BM25 query after pruning.")
        #     return

        # # 4. Combine or display final results
        # final_text = "\n---\n".join(bm25_chunks)

        # print("==== PRUNED OUTPUT (first pass) ====")
        # print(pruned_html, "... (truncated)")  # preview

        # print("\n==== BM25 OUTPUT (second pass) ====")
        # print(final_text, "... (truncated)")

if __name__ == "__main__":
    asyncio.run(main())