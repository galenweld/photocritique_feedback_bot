until python run.py; do
	echo "Bot crashed. Restarting after delay." >&2
	mail -s "Photocritique Bot crashed from command line" gweld@cs.washington.edu < /dev/null
	sleep 300
done
