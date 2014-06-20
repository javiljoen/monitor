#!/bin/bash

python -c 'for i in range(1000000): print(i * 10)' \
	| sed 's/0$/5/' \
	| tr 5 A \
	> /dev/null

