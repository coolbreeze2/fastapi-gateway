if [ ! -f .env.yaml ]; then
  touch .env.yaml
fi;
python wsgi.py