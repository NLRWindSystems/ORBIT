rm -rf _build
jupyter-book build .

cp -f _build/jupyter_execute/**/*.ipynb ../examples/
nb_file_names=$(find _build/jupyter_execute/**/*.ipynb -type f | awk -F/ 'BEGIN {ORS=" "} {print $NF}')

cd ../examples
jupyter nbconvert --clear-output --inplace $nb_file_names
pre-commit run --files $nb_file_names
cd ../docs
