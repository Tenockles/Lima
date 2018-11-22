.. _get_source:

Get the Source
--------------
As Lima is not packaged yet, the only way for now is to retrieve the source from Github. You may either get the source tarball from the releases or use Git_.

Recent version of Git_ are provided by Conda, so if you already have Conda, you may want to install it in your base environment:

.. code-block:: bash

  conda install git

Else, for both Linux and Windows, we recommend to use the git tools:

- For Linux, install Git_ package if your linux distribution did not.
- For Windows, get and install Git_ first from the download section. Then use the git-bash tool with linux-like commands.

All cameras
^^^^^^^^^^^

Here is the command to get the sources for all cameras:

.. code-block:: bash

  git clone --recursive git://github.com/esrf-bliss/Lima.git

For a specific camera
^^^^^^^^^^^^^^^^^^^^^

Here are the commands for a minimum checkout to get all source needed for a specific camera:

.. code-block:: bash

  git clone git://github.com/esrf-bliss/Lima.git
  cd Lima
  git submodule init third-party/Processlib third-party/Sps third-party/libconfig
  git submodule init camera/CAMERA_YOU_WANT_TO_COMPILE
  git submodule update

In addition (but optional) you can get the **TANGO** python device servers, so update your git clone again:

.. code-block:: bash

  git submodule init applications/tango/python
  git submodule update

For a Specific Version
^^^^^^^^^^^^^^^^^^^^^^
Stable versions of lima are tracked via Git branches and Git tags. So you can retrieve any particular version using git tools.
Please refer to the release notes document `release notes`_ , for more information of the latest release and tags.

For instance if you want to get version 1.8.0 of Lima core, do:

.. code-block:: bash

  git checkout v1.8.0
  git submodule init
  git submodule update


.. _git: https://git-scm.com
.. _release notes: ./ReleaseNotes.txt
