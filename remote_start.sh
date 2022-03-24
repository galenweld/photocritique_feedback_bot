#!/bin/bash
tmux new-session -d -s pcbot;                        # start detached tmux session
tmux split-window;                                   # split the detached tmux session
tmux send 'conda activate pcbot' ENTER;              # ativate the conda environment
tmux send 'cd ~/photocritique_feedback_bot' ENTER;   # cd to the right directory
tmux send 'python run.py' ENTER;                     # start the bot running
