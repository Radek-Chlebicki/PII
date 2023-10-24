import subprocess

# List of strings to replace XXX
strings = ["entertainment", "online_shopping", "games", "travel", "general_news", "sports"]

# Loop through the list of strings and call the Python command
for str_val in strings:
    # source_dir = f"hars_{str_val}/"
    source_dir = f"hars_{str_val}_cloak_new/"
    dest_file = f"hars_{str_val}_cloak_redo.csv"
    try:
        # Construct the command as a list
        command = ["python", "python_scripts/getLeaks.py", source_dir, "final_hashes.csv",dest_file]

        # Call the command
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing the command for {str_val}: {e}")
