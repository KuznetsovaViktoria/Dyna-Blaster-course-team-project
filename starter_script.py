import subprocess

scripts = ['server.py', 'client_for_bot.py','client_for_bot.py','client_for_bot.py', 'client_for_bot.py']
processes = []
for script in scripts:
    processes.append(subprocess.Popen(['python', script]))
for process in processes:
    process.wait()