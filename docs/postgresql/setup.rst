=======================
 Setting Up PostgreSQL
=======================

.. highlight:: shell


If you installed PostgreSQL from a binary package, you probably have a
user account named ``postgres``. Since PostgreSQL respects the name of
the logged-in user by default, switch to the ``postgres`` account to
create the RelStorage user and database. Even ``root`` does not have
the PostgreSQL privileges that the ``postgres`` account has. For
example::

    $ sudo su - postgres
    $ createuser --pwprompt zodbuser
    $ createdb -O zodbuser zodb

Alternately, you can use the ``psql`` PostgreSQL client and issue SQL
statements to create users and databases. For example::

    $ psql -U postgres -c "CREATE USER zodbuser WITH PASSWORD 'relstoragetest';"
    $ psql -U postgres -c "CREATE DATABASE zodb OWNER zodbuser;"

New PostgreSQL accounts often require modifications to ``pg_hba.conf``,
which contains host-based access control rules. The location of
``pg_hba.conf`` varies, but ``/etc/postgresql/8.4/main/pg_hba.conf`` is
common. PostgreSQL processes the rules in order, so add new rules
before the default rules rather than after. Here is a sample rule that
allows only local connections by ``zodbuser`` to the ``zodb``
database::

    local  zodb  zodbuser  md5

PostgreSQL re-reads ``pg_hba.conf`` when you ask it to reload its
configuration file::

    /etc/init.d/postgresql reload
