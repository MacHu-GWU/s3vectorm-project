
.. image:: https://readthedocs.org/projects/s3vectorm/badge/?version=latest
    :target: https://s3vectorm.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/s3vectorm-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/MacHu-GWU/s3vectorm-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/s3vectorm-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/s3vectorm-project

.. image:: https://img.shields.io/pypi/v/s3vectorm.svg
    :target: https://pypi.python.org/pypi/s3vectorm

.. image:: https://img.shields.io/pypi/l/s3vectorm.svg
    :target: https://pypi.python.org/pypi/s3vectorm

.. image:: https://img.shields.io/pypi/pyversions/s3vectorm.svg
    :target: https://pypi.python.org/pypi/s3vectorm

.. image:: https://img.shields.io/badge/✍️_Release_History!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/s3vectorm-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/⭐_Star_me_on_GitHub!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/s3vectorm-project

------

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://s3vectorm.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/s3vectorm-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/s3vectorm-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/s3vectorm-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/s3vectorm#files


Welcome to ``s3vectorm`` Documentation
==============================================================================
.. image:: https://s3vectorm.readthedocs.io/en/latest/_static/s3vectorm-logo.png
    :target: https://s3vectorm.readthedocs.io/en/latest/

``s3vectorm`` is a Python ORM-style library that provides a type-safe, intuitive interface for managing vector data in AWS S3 Vectors service. Built on top of Pydantic, it combines the power of AWS's cost-effective vector storage with the reliability of runtime type validation and the familiarity of ORM-like data manipulation.

**Why S3 Vectors + s3vectorm?**

AWS S3 Vectors offers up to 90% cost reduction compared to traditional vector databases, making it an ideal choice for startups and cost-conscious organizations building RAG (Retrieval-Augmented Generation) applications. However, working directly with the AWS SDK can be verbose and error-prone. ``s3vectorm`` bridges this gap by providing a clean, Pythonic API that makes vector operations as simple as working with traditional database models.

**Type-Safe Vector Models**

Define your vector data structures using familiar Pydantic syntax with automatic validation:

.. code-block:: python

    from s3vectorm import Vector
    from pydantic import Field

    class DocumentChunk(Vector):
        document_id: str = Field(description="Source document ID")
        chunk_seq: int = Field(description="Chunk sequence number")
        title: str = Field(description="Document title")
        category: str = Field(description="Document category")
        owner_id: str = Field(description="Document owner")

**Intuitive Query Builder**

Build complex metadata queries using a SQLAlchemy-inspired syntax:

.. code-block:: python

    from s3vectorm import BaseMetadata, MetaKey

    class DocumentMeta(BaseMetadata):
        document_id = MetaKey()
        category = MetaKey()
        owner_id = MetaKey()

    # Build queries naturally
    filter_query = (
        DocumentMeta.category.eq("research") &
        DocumentMeta.owner_id.in_(["alice", "bob"])
    )

**Ready for Production RAG**

With ``s3vectorm``, you can build sophisticated RAG applications in minutes, not days. The library handles the complexities of AWS S3 Vectors operations while providing the type safety and developer experience you expect from modern Python libraries. Whether you're prototyping your first vector search feature or scaling to millions of embeddings, ``s3vectorm`` provides the foundation for reliable, cost-effective vector operations.


.. _install:

Install
------------------------------------------------------------------------------

``s3vectorm`` is released on PyPI, so all you need is to:

.. code-block:: console

    $ pip install s3vectorm

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade s3vectorm
