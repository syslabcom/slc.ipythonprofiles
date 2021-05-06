# -*- coding: utf-8 -*-
import os
import scorched
import textwrap

try:
    # IPython <= 0.10
    from IPython.ipapi import get as get_inst
except ImportError:
    # IPython >= 0.11
    from IPython.core.interactiveshell import InteractiveShell
    get_inst = InteractiveShell.instance


def main():
    solr_url = os.environ.get("SOLR_URL")
    solr = scorched.SolrInterface(solr_url)

    def query(*args, **kwargs):
        return list(solr.query(*args, **kwargs).execute())

    ip = get_inst()
    print(textwrap.dedent("""
        Solr mode IPython shell.

            Bound names:
              solr
              query (convenience for list(solr.query(...).execute()))
    """))
    ip.user_ns.update(dict(solr=solr, query=query))
