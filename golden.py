import os
os.system("git checkout golden")
<<<<<<< HEAD
os.system("git pull origin dev")
os.system("git add .")
os.system('git commit -m "merge from dev"')
=======
os.system("git pull origin master")
os.system("git add .")
os.system('git commit -m "merge from master to golden"')
>>>>>>> 616475f7c8905c80c2ba521566442491d7dfcc85
os.system("git push origin golden")
os.system("git checkout dev")