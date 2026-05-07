# Script to add debug output to run_CM_utils.py
with open('C:/Users/gmu_a/dev/BCP/BCP/utils/run_CM_utils.py', 'r') as f:
    content = f.read()

# Replace the first occurrence in run_CM function
old_cm_run = '''    print(cmdline)
    p = Popen(
        "cmd /c " + cmdline,
        cwd=exe_file_dir,
        shell=True,
        stdout=PIPE,
        stderr=PIPE,
    )
    try:
        stdout, stderr = p.communicate(timeout=TIMEOUT_SECONDS)
        print("stdout:", stdout.decode())
        print("stderr:", stderr.decode())
    except TimeoutExpired:
        # Handle timeout
        print("Command timed out. Terminating the process.")
        p.terminate()  # Terminate the process'''

new_cm_run = '''    print("------- [CM run_CM] -------")
    print(f">    Command: {cmdline}")
    print(f">    Working directory: {exe_file_dir}")
    p = Popen(
        "cmd /c " + cmdline,
        cwd=exe_file_dir,
        shell=True,
        stdout=PIPE,
        stderr=PIPE,
    )
    try:
        stdout, stderr = p.communicate(timeout=TIMEOUT_SECONDS)
        print("------- [CM run_CM stdout] -------")
        if stdout:
            for line in stdout.decode('utf-8', errors='ignore').split('\\n'):
                if line.strip():
                    print(f">    {line}")
        else:
            print(">    (no stdout)")
        print("------- [CM run_CM stderr] -------")
        if stderr:
            for line in stderr.decode('utf-8', errors='ignore').split('\\n'):
                if line.strip():
                    print(f">    {line}")
        else:
            print(">    (no stderr)")
        print("------- [CM run_CM end] -------")
    except TimeoutExpired:
        # Handle timeout
        print(">    Command timed out. Terminating the process.")
        p.terminate()  # Terminate the process
        print("------- [CM run_CM end] -------")'''

content = content.replace(old_cm_run, new_cm_run)

with open('C:/Users/gmu_a/dev/BCP/BCP/utils/run_CM_utils.py', 'w') as f:
    f.write(content)

print("Successfully updated run_CM_utils.py!")
