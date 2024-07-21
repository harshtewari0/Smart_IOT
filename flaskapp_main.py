from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

# Path to the FastDownward executable
FASTDOWNWARD_PATH = '/Users/neeharannavaram/Desktop/werkstudent4/downward/fast-downward.py'

@app.route('/plan', methods=['POST'])
def plan():
    try:
        # Save the PDDL files
        domain_pddl = request.files['domain'].read()
        problem_pddl = request.files['problem'].read()
        
        # Define the paths for PDDL files and result file
        directory = '/Users/neeharannavaram/Desktop/IOT/sensor/tempHum'
        domain_path = os.path.join(directory, 'humDom.pddl')
        problem_path = os.path.join(directory, 'humProb.pddl')
        result_file = os.path.join(directory, 'sas_plan.1')

        with open(domain_path, 'wb') as f:
            f.write(domain_pddl)
        with open(problem_path, 'wb') as f:
            f.write(problem_pddl)

        # Run FastDownward
        result = subprocess.run(
            ['python3', FASTDOWNWARD_PATH, '--alias', 'seq-sat-lama-2011', domain_path, problem_path],
            capture_output=True,
            text=True
        )

        # Check for errors in the execution
        if result.returncode != 0:
            return jsonify({'error': 'Error in FastDownward execution', 'details': result.stderr}), 500

        # Check if `sas_plan.1` exists and read it
        if not os.path.exists(result_file):
            return jsonify({'error': 'Plan file not found'}), 500
        
        with open(result_file, 'r') as f:
            plan_content = f.read()

        return jsonify({'plan': plan_content})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    #finally:
        # Clean up files
        #for file_name in [domain_path, problem_path, result_file]:
        #    if os.path.exists(file_name):
        #        os.remove(file_name)

if __name__ == '__main__':
    app.run(debug=True)
