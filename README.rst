=============================================================
Infrastructure-as-code for IRIS Scientific OpenStack Workshop
=============================================================

This project provides Ansible playbooks defining the virtual infrastructure
used for the IRIS Scientific OpenStack workshop.

Preparation
===========

.. code-block::

   $ virtualenv venv
   $ source venv/bin/activate
   $ pip install -U pip
   $ pip install -r requirements.txt

Install Ansible role dependencies from Ansible Galaxy:

.. code-block::

   $ source venv/bin/activate
   $ ansible-galaxy install \
       -p ansible/roles \
       -r requirements.yml

Usage
=====

First, ensure that OpenStack authentication environment variables are set,
typically by sourcing an OpenStack environment file.

.. code-block::

   $ source venv/bin/activate
   $ ansible-playbook \
       -i ansible/inventory \
       ansible/iris-workshop-infra.yml

You can use the following tags via ``-t <tag>`` to perform a subset of the
tasks:

* project
* networks
* proxy
* labs
