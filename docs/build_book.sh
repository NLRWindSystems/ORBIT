rm -rf _build
jupyter-book build . > build_log.txt

cp -f _build/jupyter_execute/**/*.ipynb ../examples/
nb_file_names=$(find _build/jupyter_execute/**/*.ipynb -type f | awk -F/ 'BEGIN {ORS=" "} {print $NF}')

cd ../examples
python ../docs/clean_notebook.py $nb_file_names
pre-commit run --files $nb_file_names

cd ../docs
printf "\nORBIT documentation built succesfully, and updated examples have been copied into ORBIT/examples/ and validated\n"
tail -n 15 build_log.txt
rm -rf build_log.txt
