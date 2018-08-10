#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

PS1='[\u@\h \W]\$ '

BROWSER=/usr/bin/chromium
EDITOR=/usr/bin/vim

export DISPLAY=":0.0"
alias ls='ls -lah --color=auto'
alias flush='cat /dev/null > ~/.bash_history && history -c && exit'

# Creates a new github repository in pwd
alias ghub='python ../Python/ghub.py'
