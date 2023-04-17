import os
import json
import subprocess

def process_uploaded_file(file_path, exercise):
    filename = exercise.title
    code = exercise.source_code
    config = exercise.config_code
    unittest = exercise.unittest

    if config.strip() == '' or unittest.strip() == '':
        return None

    with open(os.path.join(file_path, f"{filename}.py"), 'w') as outfile:
        outfile.write(code)
    with open(os.path.join(file_path, f"{filename}.yaml"), 'w') as outfile:
        outfile.write(config)
    with open(os.path.join(file_path, f"{filename}_tests.py"), 'w') as outfile:
        outfile.write(unittest)

    results = os.path.join(file_path, 'results.json')

    cmd = ['python3', '-m', 'graderutils.main', f"{filename}.yaml", '--develop-mode']
    with open(results, 'w') as outfile:
        subprocess.run(cmd, stdout=outfile)
    with open(results, 'r') as infile:
        data = json.load(infile)

    return data