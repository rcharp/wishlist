import os
os.system("git checkout golden")
os.system("git pull origin dev")
os.system("git add .")
os.system('git commit -m "merge from dev"')
os.system("git push origin golden")
os.system("git checkout dev")