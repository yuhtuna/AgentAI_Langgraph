import os
import pprint
from dotenv import load_dotenv
from .graph import create_workflow

# Load environment variables from .env file at the very start
load_dotenv()


def main():
    """
    Main function to run the LangGraph workflow.
    The output of the execution will be saved to a Markdown file in the 'output' directory,
    including a Mermaid diagram of the workflow.
    """
    # --- 1. Setup Output Directory and File ---
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    i = 1
    while os.path.exists(os.path.join(output_dir, f"sample{i}.md")):
        i += 1
    output_filename = os.path.join(output_dir, f"sample{i}.md")

    # --- 2. Create workflow and graph diagram ---
    app = create_workflow()
    try:
        # Generate a Mermaid diagram of the graph
        mermaid_graph = app.get_graph().draw_mermaid()
    except Exception as e:
        mermaid_graph = f"Error generating graph: {e}"


    # --- 3. Execute Workflow and Save Output ---
    print(f"Running workflow... Output will be saved to {output_filename}")
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        # Write the diagram to the markdown file
        f.write("# Agent Workflow Diagram\n\n")
        f.write("```mermaid\n")
        f.write(mermaid_graph)
        f.write("\n```\n\n")
        f.write("---\n\n")

        # Configuration for the graph execution
        config = {"recursion_limit": 50}
        inputs = {"task": "Write a report on the latest advancements in AI as of July 2025."}
    
        # Run the graph and stream the results into the markdown file
        f.write(f"# AI Agent Execution Log for Task: \"{inputs['task']}\"\n\n")
        for event in app.stream(inputs, config=config):
            for node_name, state_update in event.items():
                f.write(f"## ➡️ Executing Node: `{node_name}`\n\n")
                # The state_update is a dictionary, e.g., {'plan': '...'}
                # We just want the text content from it.
                for content in state_update.values():
                    if isinstance(content, str):
                        # The content from the LLM is already in markdown format.
                        f.write(content)
                    else:
                        # Fallback for non-string content
                        f.write("```json\n")
                        f.write(pprint.pformat(content))
                        f.write("\n```")
                f.write("\n\n---\n\n")

    print(f"Successfully saved output to {output_filename}")


if __name__ == "__main__":
    main()
