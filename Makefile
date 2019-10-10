test:
	(ls std_4_9.json stixinfra.py) | (. ./p/bin/activate && ~/src/eradman-entr-c15b0be493fc/entr sh -c 'python -m coverage run -m unittest stixinfra && python -m coverage report -m --omit=p/\*')

setupenv:
	virtualenv-2.7 p && \
	( . ./p/bin/activate && pip install -r requirements.txt)
