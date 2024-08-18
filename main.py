# Main script to run other scripts

# Define a list of script filenames to be executed
scripts = ['scraper.py', 'scraper_v2.py']

# Loop through the scripts and execute each one
for script in scripts:
    with open(script, 'r') as file:
        exec(file.read())