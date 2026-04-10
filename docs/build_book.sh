rm -rf _build
jupyter-book build .
cp -f _build/jupyter_execute/tutorials/*.ipynb ../examples/
cp -f _build/jupyter_execute/topical_guides/*.ipynb ../examples/
