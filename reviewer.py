import os
import sys
from github import Github, Auth
from google import genai

# Fetch environment variables supplied by GitHub Actions
github_token = os.getenv("GITHUB_TOKEN")
api_key = os.getenv("GEMINI_API_KEY")
pr_number_str = os.getenv("PR_NUMBER")
repo_name = os.getenv("GITHUB_REPOSITORY")

if not api_key:
    print("Error: GEMINI_API_KEY environment variable is missing or empty.")
    sys.exit(1)

if not pr_number_str or not repo_name:
    print("Not running inside a Pull Request context.")
    sys.exit(0)

pr_number = int(pr_number_str)

# Initialize GitHub Client
auth = Auth.Token(github_token)
gh = Github(auth=auth)

# Initialize Gemini Client
client = genai.Client(api_key=api_key)

repo = gh.get_repo(repo_name)
pr = repo.get_pull(pr_number)

# Extract Diff
diff_text = ""
for file in pr.get_files():
    if file.status in ["added", "modified"]:
        diff_text += f"\n--- File: {file.filename} ---\n{file.patch}\n"

if not diff_text.strip():
    prinrt("No relevant code additions or modifications found.")
    sys.exit(0)

prompt = f"""
You are an expert senior software engineer conducting an automated code review.
Review the following Git diff for code quality, potential security flaws, bugs, and performance optimizations.
Provide clear, actionable feedback with code suggestions where appropriate.

Git Diff:
{diff_text[:4000]}
"""

# Generate Review using Gemini 2.5 Flash
# Change this line:
response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents=prompt,
)

review_comment = response.text

# Post comment to PR
pr.create_issue_comment(f"### 🤖 AI Code Review Summary (Powered by Gemini)\n\n{review_comment}")
print("Review posted successfully to the Pull Request!")

# Replace the generation block in reviewer.py with this:
models_to_try = ["gemini-3.8-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
review_comment = None

for model_name in models_to_try:
    try:
        print(f"Attempting review with {model_name}...")
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        review_comment = response.text
        print(f"Successfully generated review with {model_name}")
        break
    except Exception as e:
        print(f"Model {model_name} failed: {e}")

if not review_comment:
    print("All models failed to respond.")
    sys.exit(1)

# Post comment to PR
pr.create_issue_comment(f"### 🤖 AI Code Review Summary (Powered by Gemini)\n\n{review_comment}")
print("Review posted successfully to the Pull Request!")