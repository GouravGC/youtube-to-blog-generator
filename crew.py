
import time

import tiktoken
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task
from langsmith import traceable

load_dotenv()


# --------------------------------------------------
# TOKEN COUNTING
# --------------------------------------------------

def count_tokens(text: str) -> int:
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


# --------------------------------------------------
# 1. RESEARCHER AGENT EXECUTION
# --------------------------------------------------

@traceable(
    name="researcher_agent",
    run_type="chain",
    process_inputs=lambda inputs: {
        **inputs,
        "transcript": (
            f"[Transcript redacted: "
            f"{len(inputs.get('transcript', ''))} characters]"
        )
    }
)
def run_researcher(video_url: str, video_title: str, transcript: str):

    from agents import blog_researcher
    from tasks import create_tasks

    research_task, _ = create_tasks()

    research_crew = Crew(
        agents=[blog_researcher],
        tasks=[research_task],
        process=Process.sequential,
        memory=False,
        cache=True,
        verbose=True
    )

    result = research_crew.kickoff(
        inputs={
            "video_url": video_url,
            "video_title": video_title,
            "transcript": transcript
        }
    )

    research_notes = result.raw.strip()

    if not research_notes:
        raise ValueError("Researcher returned empty research notes.")

    return research_notes


# --------------------------------------------------
# 2. WRITER AGENT EXECUTION
# --------------------------------------------------

@traceable(
    name="writer_agent",
    run_type="chain"
)
def run_writer(
    video_title: str,
    research_notes: str,
    writer_description: str,
    expected_output: str
):

    from agents import blog_writer

    description = writer_description.replace(
        "{video_title}",
        video_title
    )

    description += (
        "\n\nRESEARCH NOTES FROM THE RESEARCHER:\n"
        f"{research_notes}\n\n"
        "Use only these research notes as factual source material."
    )

    writer_task = Task(
        description=description,
        expected_output=expected_output,
        agent=blog_writer,
        async_execution=False
    )

    writer_crew = Crew(
        agents=[blog_writer],
        tasks=[writer_task],
        process=Process.sequential,
        memory=False,
        cache=False,
        verbose=True
    )

    result = writer_crew.kickoff()

    blog = result.raw.strip()

    if not blog:
        raise ValueError("Writer returned an empty blog.")

    token_count = count_tokens(blog)

    print(f"\nInitial blog token count: {token_count}")

    # One revision attempt if the blog exceeds 400 tokens.
    if token_count > 400:

        print("Blog exceeds 400 tokens. Requesting revision...")

        revision_task = Task(
            description=(
                "Rewrite this blog to contain 300-400 tokens, "
                "including its title.\n\n"
                "Preserve the important technical information.\n"
                "Use only facts from the original blog.\n"
                "Do not introduce new facts or examples.\n"
                "Return only the revised Markdown blog.\n\n"
                f"ORIGINAL BLOG:\n{blog}"
            ),
            expected_output=(
                "A concise Markdown blog of 300-400 tokens."
            ),
            agent=blog_writer,
            async_execution=False
        )

        revision_crew = Crew(
            agents=[blog_writer],
            tasks=[revision_task],
            process=Process.sequential,
            memory=False,
            cache=False,
            verbose=True
        )

        revised_result = revision_crew.kickoff()
        revised_blog = revised_result.raw.strip()
        revised_count = count_tokens(revised_blog)

        print(f"Revised blog token count: {revised_count}")

        if abs(revised_count - 350) < abs(token_count - 350):
            blog = revised_blog
            token_count = revised_count

    print(f"Final blog token count: {token_count}")

    return {
        "blog": blog,
        "token_count": token_count
    }


# --------------------------------------------------
# 3. FINAL WORKFLOW OUTPUT
# --------------------------------------------------

@traceable(
    name="final_workflow_output",
    run_type="chain"
)
def record_final_output(
    video_title: str,
    blog: str,
    token_count: int,
    execution_time: float
):

    return {
        "status": "success",
        "video_title": video_title,
        "blog": blog,
        "token_count": token_count,
        "execution_time_seconds": round(execution_time, 2)
    }


# --------------------------------------------------
# PARENT WORKFLOW
# --------------------------------------------------

@traceable(
    name="youtube_blog_workflow",
    run_type="chain",
    process_inputs=lambda inputs: {
        **inputs,
        "transcript": (
            f"[Transcript redacted: "
            f"{len(inputs.get('transcript', ''))} characters]"
        )
    }
)
def generate_blog(
    video_url: str,
    video_title: str,
    transcript: str
):

    from tasks import create_tasks

    start_time = time.perf_counter()

    # Create the original task definitions.
    _, write_task = create_tasks()

    # Stage 1: Researcher.
    research_notes = run_researcher(
        video_url=video_url,
        video_title=video_title,
        transcript=transcript
    )

    # Stage 2: Writer.
    writer_result = run_writer(
        video_title=video_title,
        research_notes=research_notes,
        writer_description=write_task.description,
        expected_output=write_task.expected_output
    )

    blog = writer_result["blog"]
    token_count = writer_result["token_count"]

    execution_time = time.perf_counter() - start_time

    # Stage 3: Final output.
    final_result = record_final_output(
        video_title=video_title,
        blog=blog,
        token_count=token_count,
        execution_time=execution_time
    )

    print("\n========== WORKFLOW SUMMARY ==========")
    print("Status:", final_result["status"])
    print("Video:", video_title)
    print("Blog tokens:", token_count)
    print("Execution time:", final_result["execution_time_seconds"], "seconds")
    print("======================================")

    return final_result["blog"]
