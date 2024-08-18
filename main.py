import os
from dotenv import load_dotenv
from git import Repo

# Load environment variables from .env file (if you have any sensitive data or configuration there)
load_dotenv()

# Define a list of script filenames to be executed
scripts = ['scraper.py', 'scraper_v2.py']

# Function to run other scripts
def run_scripts(scripts):
    for script in scripts:
        try:
            with open(script, 'r') as file:
                exec(file.read())
            print(f"Successfully executed {script}")
        except Exception as e:
            print(f"Error executing {script}: {e}")

# Function to commit and push changes to GitHub
def git_commit_and_push(repo_path, commit_message):
    try:
        # Open the Git repository
        repo = Repo(repo_path)
        if repo.is_dirty(untracked_files=True):
            # Stage all changes (including new files)
            repo.git.add(all=True)
            
            # Commit the changes
            repo.index.commit(commit_message)
            
            # Push to the remote repository
            origin = repo.remote(name='origin')
            origin.push()
            
            print("Changes have been committed and pushed to the repository.")
        else:
            print("No changes to commit.")
    except Exception as e:
        print(f"An error occurred while committing and pushing changes: {e}")

if __name__ == "__main__":
    # Define the path to your local Git repository
    repo_path = os.path.abspath(os.path.dirname(__file__))  # This assumes your script is in the repo root
    
    # Define the commit message
    commit_message = "Automated commit after script execution"
    
    # Run the scripts
    run_scripts(scripts)
    
    # Commit and push changes
    git_commit_and_push(repo_path, commit_message)
