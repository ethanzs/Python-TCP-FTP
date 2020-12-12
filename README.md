# Python TCP FTP Program
A simple TCP FTP program written in python. It has two sockets: one for commands and one for data. Both are TCP sockets.

## Start Each Program
> python server.py [command port] [data port]
> python client.py [server ip] [command port] [data port]

## Commands
> ls
> cd [into]
> get [file]
> put [file]