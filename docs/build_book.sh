rm -rf _build
jupyter-book build .
cp -f _build/jupyter_execute/tutorial/*.ipynb ../examples/
