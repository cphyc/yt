How to Do a Release
-------------------

Periodically, the yt development community issues new releases. Since yt follows
`semantic versioning <http://semver.org/>`_, the type of release can be read off
from the version number used. Version numbers should follow the scheme
``MAJOR.MINOR.PATCH``. There are three kinds of possible releases:

* Bugfix releases

  These releases are regularly scheduled and will optimally happen approximately
  once a month. These releases should contain only fixes for bugs discovered in
  earlier releases and should not contain new features or API changes. Bugfix
  releases should increment the ``PATCH`` version number. Bugfix releases should
  *not* be generated by merging from the ``yt`` branch, instead bugfix pull
  requests should be manually backported using the PR backport script, described
  below. Version ``3.2.2`` is a bugfix release.

* Minor releases

  These releases happen when new features are deemed ready to be merged into the
  ``stable`` branch and should not happen on a regular schedule. Minor releases
  can also include fixes for bugs if the fix is determined to be too invasive
  for a bugfix release. Minor releases should *not* inlucde
  backwards-incompatible changes and should not change APIs.  If an API change
  is deemed to be necessary, the old API should continue to function but might
  trigger deprecation warnings. Minor releases should happen by merging the
  ``yt`` branch into the ``stable`` branch. Minor releases should increment the
  ``MINOR`` version number and reset the ``PATCH`` version number to zero.
  Version ``3.3.0`` is a minor release.

* Major releases

  These releases happen when the development community decides to make major
  backwards-incompatible changes. In principle a major version release could
  include arbitrary changes to the library. Major version releases should only
  happen after extensive discussion and vetting among the developer and user
  community. Like minor releases, a major release should happen by merging the
  ``yt`` branch into the ``stable`` branch. Major releases should increment the
  ``MAJOR`` version number and reset the ``MINOR`` and ``PATCH`` version numbers
  to zero. If it ever happens, version ``4.0.0`` will be a major release.

The job of doing a release differs depending on the kind of release. Below, we
describe the necessary steps for each kind of release in detail.

Doing a Bugfix Release
~~~~~~~~~~~~~~~~~~~~~~

As described above, bugfix releases are regularly scheduled updates for minor
releases to ensure fixes for bugs make their way out to users in a timely
manner. Since bugfix releases should not include new features, we do not issue
bugfix releases by simply merging from the development ``yt`` branch into the
``stable`` branch.  Instead, we make use of the ``pr_backport.py`` script to
manually cherry-pick bugfixes from the from ``yt`` branch onto the ``stable``
branch.

The backport script issues interactive prompts to backport individual pull
requests to the ``stable`` branch in a temporary clone of the main yt mercurial
repository on bitbucket. The script is written this way to to avoid editing
history in a clone of the repository that a developer uses for day-to-day work
and to avoid mixing work-in-progress changes with changes that have made their
way to the "canonical" yt repository on bitbucket.

Rather than automatically manipulating the temporary repository by scripting
mercurial commands using ``python-hglib``, the script must be "operated" by a
human who is ready to think carefully about what the script is telling them
to do. Most operations will merely require copy/pasting a suggested mercurial
command. However, some changes will require manual backporting.

To run the backport script, first open two terminal windows. The first window
will be used to run the backport script. The second terminal will be used to
manipulate a temporary clone of the yt mercurial repository. In the first
window, navigate to the ``scripts`` directory at the root of the yt repository
and run the backport script,

.. code-block:: bash

   $ cd $YT_HG/scripts
   $ python pr_backport.py

You will then need to wait for about a minute (depending on the speed of your
internet connection and bitbucket's servers) while the script makes a clone of
the main yt repository and then gathers information about pull requests that
have been merged since the last tagged release. Once this step finishes, you
will be prompted to navigate to the temporary folder in a new separate terminal
session. Do so, and then hit the enter key in the original terminal session.

For each pull request in the set of pull requests that were merged since the
last tagged release that were pointed at the "main" line of development
(e.g. not the ``experimental`` bookmark), you will be prompted by the script
with the PR number, title, description, and a suggested mercurial
command to use to backport the pull request. If the pull request consists of a
single changeset, you will be prompted to use ``hg graft``. If it contains more
than one changeset, you will be prompted to use ``hg rebase``. Note that
``rebase`` is an optional extension for mercurial that is not turned on by
default. To enable it, add a section like the following in your ``.hgrc`` file:

.. code-block:: none

   [extensions]
   rebase=

Since ``rebase`` is bundled with core mercurial, you do not need to specify a
path to the rebase extension, just say ``rebase=`` and mercurial will find the
version of ``rebase`` bundled with mercurial. Note also that mercurial does not
automatically update to the tip of the rebased head after executing ``hg
rebase`` so you will need to manually issue ``hg update stable`` to move your
working directory to the new head of the stable branch. The backport script
should prompt you with a suggestion to update as well.

If the pull request contains merge commits, you must take care to *not* backport
commits that merge with the main line of development on the ``yt`` branch. Doing
so may bring unrelated changes, including new features, into a bugfix
release. If the pull request you'd like to backport contains merge commits, the
backport script should warn you to be extra careful.

Once you've finished backporting, the script will let you know that you are done
and warn you to push your work. The temporary repository you have been working
with will be deleted as soon as the script exits, so take care to push your work
on the ``stable`` branch to your fork on bitbucket. Once you've pushed to your
fork, you will be able to issue a pull request containing the backported fixes
just like any other yt pull request.

Doing a Minor or Major Release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is much simpler than a bugfix release.  All that needs to happen is the
``yt`` branch must get merged into the ``stable`` branch, and any conflicts that
happen must be resolved, almost certainly in favor of the yt branch. This can
happen either using a merge tool like ``vimdiff`` and ``kdiff3`` or by telling
mercurial to write merge markers. If you prefer merge markers, the following
configuration options should be turned on in your ``hgrc`` to get more detail
during the merge:

.. code-block:: none

   [ui]
   merge = internal:merge3
   mergemarkers = detailed

The first option tells mercurial to write merge markers that show the state of
the conflicted region of the code on both sides of the merge as well as the
"base" most recent common ancestor changeset. The second option tells mercurial
to add extra information about the code near the merge markers.


Incrementing Version Numbers and Tagging a Release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before creating the tag for the release, you must increment the version numbers
that are hard-coded in a few files in the yt source so that version metadata
for the code is generated correctly. This includes things like ``yt.__version__``
and the version that gets read by the Python Package Index (PyPI) infrastructure.

The paths relative to the root of the repository for the three files that need
to be edited are:

* ``doc/source/conf.py``

  The ``version`` and ``release`` variables need to be updated.

* ``setup.py``

  The ``VERSION`` variable needs to be updated

* ``yt/__init__.py``

  The ``__version__`` variable must be updated.

Once these files have been updated, commit these updates. This is the commit we
will tag for the release.

To actually create the tag, issue the following command:

.. code-block:: bash

   hg tag <tag-name>

Where ``<tag-name>`` follows the project's naming scheme for tags
(e.g. ``yt-3.2.1``). Commit the tag, and you should be ready to upload the
release to pypi.

If you are doing a minor or major version number release, you will also need to
update back to the development branch and update the development version numbers
in the same files.


Uploading to PyPI
~~~~~~~~~~~~~~~~~

To actually upload the release to the Python Package Index, you just need to
issue the following command:

.. code-block:: bash

   python setup.py sdist upload -r https://pypi.python.org/pypi

You will be prompted for your PyPI credentials and then the package should
upload. Note that for this to complete successfully, you will need an account on
PyPI and that account will need to be registered as an "owner" of the yt
package. Right now there are three owners: Matt Turk, Britton Smith, and Nathan
Goldbaum.

After the release is uploaded to PyPI, you should send out an announcement
e-mail to the yt mailing lists as well as other possibly interested mailing
lists for all but bugfix releases. In addition, you should contact John ZuHone
about uploading binary wheels to PyPI for Windows and OS X users and contact
Nathan Goldbaum about getting the Anaconda packages updated.