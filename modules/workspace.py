import os

def start_assessment():
    print("Preparing assessment workspace...")

    os.makedirs("sites", exist_ok=True)

    if not os.path.exists("summary.md"):
        with open("summary.md", "w") as f:
            f.write("# External Assessment Summary\n\n")

    print("Workspace ready.")
