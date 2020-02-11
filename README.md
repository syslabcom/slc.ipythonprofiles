# slc.ipythonprofiles - IPython profiles for Zope and Plone development

This is a collection of profiles for [IPython](https://pypi.org/project/ipython/), intended for [Zope](https://www.zope.org/) and [Plone](https://plone.org/) development, currently consisting of one profile - profile_zope.

## profile_zope

This profile instantiates a Zope app so that you have full access to your site from an IPython shell, i.e. you have all the niceties like auto-completion and line editing, plus a few helper methods.

### Installation

Add this to your buildout configuration:

    [buildout]
    parts =
        ipzope
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

    [sources]
    slc.ipythonprofiles = git https://github.com/syslabcom/slc.ipythonprofiles.git egg=false

### Usage

Run ipzope. The interpreter prints a few hints about what's available in the shell.

## License

This software is distributed under the [German Free Software License](http://www.d-fsl.org).

The original version of profile_zope was created by [InQuant GmbH](https://www.inquant.de/).
