from .graph import create_workflow


def main():
    """
    Main function to run the LangGraph workflow.
    We can invoke the graph with an initial state.
    The `stream` method lets us see the output of each node as it runs.
    """
    # Create and compile the workflow
    app = create_workflow()
    
    # Configuration for the graph execution
    config = {"recursion_limit": 50}
    inputs = {"task": "Write a report on the latest advancements in AI as of July 2025."}

    # Run the graph and stream the results
    for event in app.stream(inputs, config=config):
        for key, value in event.items():
            print(f"Event: '{key}'")
            print("---")
            print(value)
        print("\n---\n")


if __name__ == "__main__":
    main()
