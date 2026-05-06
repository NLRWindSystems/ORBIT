# Contributor's Guide

We welcome contributions in the form of bug reports, bug fixes, improvements to the documentation,
ideas for enhancements (or the enhancements themselves!).

You can find a [list of current issues](https://github.com/NLRWindSystems/ORBIT/issues) in the
project's GitHub repo. Feel free to tackle any existing bugs or enhancement ideas by submitting a
[pull request](https://github.com/NLRWindSystems/ORBIT/pulls).

## Installing ORBIT for Developers

Please read the
[developer's setup section of the installation guide](./getting_started/install.md#development-setup)
on the previous page for setting up a developer environment with ORBIT's developer tools.

## Bug Reports

* Please include a short (but detailed) Python snippet or explanation for reproducing the problem.
  Be sure to attach or include a link to any input files that will be needed to reproduce the error.
* Explain the behavior you expected, and how what you got differed.

## Pull Requests

* Changes should be pass the linting and autoformatting checks provided through `pre-commit`.
  If they do not, the PR's CI pipeline will fail and will block the acceptance of your
  contributions until they pass. If your commit fails, then check the `pre-commit` logs to see
  if any fixes were automatically applied or if manual changes are required. Once the changes are
  made, simply reattempt to add and commit your files.
* Keep style fixes to a separate commit to make your pull request more readable.
* Docstrings are required and should follow the
  [NumPy style](https://www.sphinx-doc.org/en/master/usage/extensions/example_numpy.html).
* When you start working on a pull request, start by creating a new branch pointing at the latest
  commit on [dev](https://github.com/NLRWindSystems/ORBIT/tree/dev) based on your own fork (i.e.,
  replace "NLRWindSystems" with your GitHub username).
* The ORBIT copyright policy is detailed in the [`LICENSE`](https://github.com/NLRWindSystems/ORBIT/blob/main/LICENSE).
* Build the docs locally, and check that the build status of all examples in the
  [tutorials](#tutorials) and [topical guides](#topical-guides). If any build fails,
  be sure to fix the newly broken functionality. See the [documentation section](#documentation)
  for more details on building the documentation

## Documentation

When contributing new features or fixing existing capabilities, be sure to add and/or update the
docstrings as needed to ensure the documentation site stays up to date with the latest changes.
Please also update any relevant guides or examples in the documentation if functionality has
changed, or if there is new functionality that should be highlighted.

### Minor Updates

To build the documentation locally, the following command can be run in your terminal in the `docs/`
directory of the repository. In general, this command should be used when the documentation does
not need to be rebuilt from scratch.

```bash
jupyter-book build .
```

### Prior to a Pull Request

When overhauling any sections of the documentation, wanting a clean build, or prior to submitting
a pull request, the following command should be run in the terminal from within the `docs/`
directory. This command encapsulates the above, but it removes any previously built versions of
the documentation, and copies over the updated Jupyter Notebook examples. The rebuilt `.ipynb`
files will all need to be added and committed to ensure the examples stay up to date with the
documentation.

```bash
sh build_book.sh
```

### Viewing the Locally Built Documentation

In addition to building the documentation, be sure to check the results by opening the following
path in your browser: `file:///<path-to-ORBIT>/ORBIT/docs/_build/html/index.html`.

```{note}
If the browser appears to be out of date from what you expected to be built, please try reloading
the page a few times. If that doesn't work, then:

1. Close the documentation tab
2. Clear your browser's cache
3. Rebuild the docs using [prior to a PR section](#prior-to-a-pull-request)
4. Open the page again.
```

### Writing Executable Content

All executable content, such as Jupyter notebooks, should be converted to the executable markdown
format used by Jupyter Book. For users that prefer to develop examples in Jupyter notebooks, then
Jupytext (separate installation required) can be used to convert their work using the following
command. For more details, please see their documentation:
https://jupytext.readthedocs.io/en/latest/using-cli.html.

```bash
jupytext notebook.ipynb --to myst
```

Similarly, any documentation example that users wish to interact with can be converted to a notebook
using the following command.

```bash
jupytext notebook.md --to .ipynb
```

## Tests

The test suite can be run using `pytest tests/`. Individual test files can be run by specifying them:

```bash
pytest tests/tes_library.py
```

and individual tests can be run within those files

```bash
pytest tests/test_library.py -k test_initialize_library
```

When you push to your fork, or open a PR, your tests will be run against the
[Continuous Integration (CI)](https://github.com/NLRWindSystems/ORBIT/actions) suite. This will start a build
that runs all tests on your branch against multiple Python versions, and will also test
documentation builds.

## Code Review Process

All pull requests will be reviewed by at least one other person before being merged into the dev
or main branch. Here are some guidelines to help with the review process, both as the person
submitting the pull request, and as the reviewer.

### Code or Documentation Contributor

* Quality is a priority -- take the time to ensure your code is clear, well-documented, and tested.
* Keep pull requests small enough to be reviewed in under 30 minutes; this helps reviewers give
  thorough feedback and makes the process more efficient.
* Value readability and understandability, but balance this with computational efficiency. Readable
  code is preferred unless a more abstract or optimized approach is clearly necessary and
  well-justified.
* Be open to discussion and feedback. If written communication becomes challenging, consider
  scheduling a call to clarify intent and resolve misunderstandings.
* Express appreciation for feedback, even if it's critical -- good reviews take time and effort.
* NLR employees, when requesting a review, notify the reviewer directly (e.g., via email or Teams)
  to ensure timely attention.
* Ask for a review, not just approval. The goal is to improve the codebase together and constructive
  feedback is an integral part of that process.

### Code Reviewer

* Test the code locally when possible to verify changes.
* Aim to either accept the pull request or request specific changes, rather than leaving only comments.
* Provide feedback constructively -- focus on the code and its functionality, not the person who wrote it.
* If you leave several critical suggestions, include positive feedback on aspects you appreciate.
* Communicate promptly once the PR author has addressed your feedback; aim to complete reviews
  within 2-3 days barring extenuating circumstances.
* Remember, communication is key -- maintain a collaborative and respectful tone throughout the process.

```{note}
Code readability and understandability are highly valued, but not if there are noticeable tradeoffs
in efficiency. Strive for a balance between clear code and appropriate performance, i.e., avoid
overly clever one liners, but vectorize and flatten control flow where possible.
```

## Release Process

### Standard

Most contributions will be into the `dev` branch, and once the threshold for a release has been
met the following steps should be taken to create a new release

1. On `dev`, bump the version appropriately, see the
   [semantic versioning guidelines](https://semver.org/) for details.
2. Open a pull request from `dev` into `main`.
3. When all CI tests pass, and the PR has been approved, merge the PR into main.
4. Pull the latest changes from GitHub into the local copy of the main branch.
5. Tag the latest commit to match the version bump in step 1 (replace "v1.2.3" in all instances
   below), and push it to the repository.

   ```bash
   git tag -a v1.2.3 -m "v1.2.3 release"
   git push --origin v1.2.3
   ```

6. Check that the
   [Test PyPI GitHub Action](https://github.com/NLRWindSystems/ORBIT/actions/workflows/publish_to_test_pypi.yml)
   has run successfully.
   1. If the action failed, identify and fix the issue, then
   2. delete the local and remote tag using the following (replace "v1.2.3" in all instances just like
      in step 5):

      ```bash
      git tag -d v1.2.3
      git push --delete origin v1.2.3
      ```

   3. Start back at step 1.
7. When the Test PyPI Action has successfully run,
   [create a new release](https://github.com/NLRWindSystems/ORBIT/releases/new) using the tag created in
   step 5.

### Patches

Any pull requests directly into the main branch that alter the H2Integrate model (excludes anything
in `docs/`, or outside of `ORBIT/` and `tests/`), should be sure to follow the instructions
below:

1. All CI tests pass and the patch version has been bumped according to the
   [semantic versioning guidelines](https://semver.org/).
2. Follow steps 4 through 7 above.
3. Merge the NLR main branch back into the develop branch and push the changes.
