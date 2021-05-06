# slc.ipythonprofiles - IPython profiles for Zope and Plone development

This is a collection of profiles for [IPython](https://pypi.org/project/ipython/), intended for [Zope](https://www.zope.org/) and [Plone](https://plone.org/) development.

## profile_zope

This profile instantiates a Zope app so that you have full access to your site from an IPython shell, i.e. you have all the niceties like auto-completion and line editing, plus a few helper methods.

## profile_metabase

This profile instantiates a Metabase API connection.

## profile_solr

This profile sets up a scorched connection to your solr instance. It also provides a convenience method `query()` which uses this connection.

### Installation

Add this to your buildout configuration:

    [buildout]
    parts =
        ipzope
        ipybase
        ipsolr
        ...
    extensions =
        mr.developer
        ...

    [ipzope]
    # a IPython Shell for interactive use with zope running.
    recipe = zc.recipe.egg
    eggs =
            ipython
            ${instance:eggs}
    initialization =
            import sys, os
            os.environ["SOFTWARE_HOME"] = " "
            os.environ["INSTANCE_HOME"] = "${instance:location}"
            os.environ["CONFIG_FILE"] = "${instance:location}/etc/zope.conf"
            os.environ["IPYTHONDIR"] = os.path.join("${buildout:directory}", "${buildout:sources-dir}", "slc.ipythonprofiles")
            sys.argv[1:1] = "--profile=zope".split()
    scripts = ipython=ipzope
    extra-paths =
        ${buildout:sources-dir}/slc.ipythonprofiles/profile_zope

    [ipsolr]
    # an IPython Shell for interactive use with a scorched connection instantiated
    recipe = zc.recipe.egg
    eggs =
            ipython
            scorched
    initialization =
            import sys, os
            os.environ["SOLR_URL"] = "http://${solr:host}:${solr:port}${solr:basepath}/core1"
            os.environ["IPYTHONDIR"] = os.path.join("${buildout:directory}", "${buildout:sources-dir}", "slc.ipythonprofiles")
            sys.argv[1:1] = "--profile=solr".split()
    scripts = ipython=ipsolr
    extra-paths =
        ${buildout:directory}/src/slc.ipythonprofiles/profile_solr

    [ipybase]
    # an IPython Shell for interactive use with the metabase api instantiated
    recipe = zc.recipe.egg
    eggs =
            ipython
            oira.statistics.deployment
    initialization =
            import sys, os
            if not "METABASE_HOST" in os.environ:
                os.environ["METABASE_HOST"] = "${metabase:metabase-host}"
            if not "METABASE_PORT" in os.environ:
                os.environ["METABASE_PORT"] = "${metabase:metabase-port}"
            if not "METABASE_USER" in os.environ:
                os.environ["METABASE_USER"] = "${metabase:metabase-user}"
            if not "METABASE_PASSWORD" in os.environ:
                os.environ["METABASE_PASSWORD"] = """${metabase:metabase-password}"""
            os.environ["IPYTHONDIR"] = os.path.join("${buildout:directory}", "${buildout:sources-dir}", "slc.ipythonprofiles")
            sys.argv[1:1] = "--profile=metabase".split()
    scripts = ipython=ipybase
    extra-paths =
        ${buildout:sources-dir}/slc.ipythonprofiles/profile_metabase

    [sources]
    slc.ipythonprofiles = git https://github.com/syslabcom/slc.ipythonprofiles.git egg=false

### Usage

Run `bin/ipzope`, `bin/ipybase` or `bin/ipsolr`. The interpreter prints a few hints about what's available in the shell.

## License

This software is distributed under the [German Free Software License](http://www.d-fsl.org).

The original version of profile_zope was created by [InQuant GmbH](https://www.inquant.de/).
