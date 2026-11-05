import tiktoken

from crewai import Crew, Process


def count_tokens(text: str) -> int:
    """Count tokens using the cl100k_base tokenizer."""

    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def generate_blog(video_url: str, video_title: str, transcript: str):

    from agents import blog_researcher, blog_writer
    from tasks import create_tasks

    research_task, write_task = create_tasks()

    crew = Crew(
        agents=[
            blog_researcher,
            blog_writer
        ],

        tasks=[
            research_task,
            write_task
        ],

        process=Process.sequential,
        memory=False,
        cache=True,
        verbose=True
    )

    result = crew.kickoff(
        inputs={
            "video_url": video_url,
            "video_title": video_title,
            "transcript": transcript
        }
    )

    blog = result.raw.strip()
    token_count = count_tokens(blog)

    print(f"\nInitial blog token count: {token_count}")

    # Request one revision if the blog exceeds the target.
    if token_count > 400:

        print("Blog exceeds 400 tokens. Requesting a shorter version...")

        revision_crew = Crew(
            agents=[blog_writer],

            tasks=[
                __import__("crewai").Task(
                    description=(
                        "Rewrite the following blog to contain "
                        "300-400 tokens, including its title.\n\n"
                        "Preserve the important technical information.\n"
                        "Do not introduce new facts or examples.\n"
                        "Do not remove essential meaning.\n"
                        "Return only the revised Markdown blog.\n\n"
                        f"ORIGINAL BLOG:\n{blog}"
                    ),
                    expected_output=(
                        "A technically accurate Markdown blog "
                        "containing 300-400 tokens."
                    ),
                    agent=blog_writer
                )
            ],

            process=Process.sequential,
            memory=False,
            cache=False,
            verbose=True
        )

        revised_result = revision_crew.kickoff()
        revised_blog = revised_result.raw.strip()
        revised_count = count_tokens(revised_blog)

        print(f"Revised blog token count: {revised_count}")

        # Use the revision only if it improves compliance.
        if 300 <= revised_count <= 400:
            blog = revised_blog

        elif abs(revised_count - 350) < abs(token_count - 350):
            blog = revised_blog

    final_count = count_tokens(blog)

    print(f"\nFinal blog token count: {final_count}")

    return blog