=============================================================
Infrastructure-as-code for IRIS Scientific OpenStack Workshop
=============================================================

This project provides Ansible playbooks defining the virtual infrastructure
used for the IRIS Scientific OpenStack workshop.

The playbooks create a single project in which all 'labs' run. Each lab is a
virtual machine connected to its own private network, accessible via a floating
IP. There is a single proxy VM which is attached to each lab's network, and
runs a Docker registry mirror, a Squid caching proxy, and a web server hosting
a CentOS7 cloud image::

             +-----------+      +-----------+      +-----------+
             |           |      |           |      |           |
             |           |      |           |      |           |
             |   Proxy   |      |   Lab 1   |      |   Lab 2   |
             |           |      |           |      |           |
             |           |      |           |      |           |
             |           |      |           |      |           |
             +--+--+--+--+      +-----+-----+      +-----+-----+
                |  |  |               |                  |
                |  |  |               |                  |
     Lab 1  +---+--------------------++--------------------------+
                   |  |              |                   |
     Lab 2  +------+------------------------------------++-------+
                      |              |                  |
     Proxy  +------+--+------------------------------------------+
                   |                 |                  |
                 +-+--+            +-+--+             +-+--+
                 | rp |            | r1 |             | r2 |
                 +-+--+            +-+--+             +-+--+
                   |                 |                  |
   External +------+-----------------+------------------+--------+

The Kayobe configuration intended to be used with this infrastructure is `here
<https://github.com/stackhpc/iris-workshop-kayobe-config>`__.

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

Configuration
=============

There are various variables that may be configured in
``ansible/group_vars/all/iris-workshop``. At a minimum, you will need to set
``iris_workshop_labs`` to a list of labs to create.

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
