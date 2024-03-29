# -*- coding: utf-8 -*-
#
# File: zdebug.py (formerly ipy_profile_zope.py)
#
# Copyright (c) InQuant GmbH
#
# An ipython profile for zope and plone. Some ideas
# stolen from http://www.tomster.org.
#
# German Free Software License (D-FSL)
#
# This Program may be used by anyone in accordance with the terms of the
# German Free Software License
# The License may be obtained under <http://www.d-fsl.org>.

from __future__ import print_function
__author__ = """Stefan Eletzhofer <stefan.eletzhofer@inquant.de>"""
__docformat__ = 'plaintext'
__revision__ = "$Revision$"

# IPython.ipapi was moved and then deprecated
try:
    # IPython <= 0.10
    from IPython.ipapi import get as get_inst
except ImportError:
    # IPython >= 0.11
    from IPython.core.interactiveshell import InteractiveShell
    get_inst = InteractiveShell.instance

import six
import sys
import os
import textwrap

# The import below effectively obsoletes your old-style ipythonrc[.ini],
# so consider yourself warned!
# import ipy_defaults

_marker = []


def shasattr(obj, attr, acquire=False):
    """ See Archetypes/utils.py
    """
    if not acquire:
        obj = obj.aq_base
    return getattr(obj, attr, _marker) is not _marker


class ZopeDebug(object):
    def __init__(self):

        self.instancehome = os.environ.get("INSTANCE_HOME")

        configfile = os.environ.get("CONFIG_FILE")
        if configfile is None and self.instancehome is not None:
            configfile = os.path.join(self.instancehome, "etc", "zope.conf")

        if configfile is None:
            raise RuntimeError("CONFIG_FILE env not set")

        print("CONFIG_FILE=", configfile)
        print("INSTANCE_HOME=", self.instancehome)

        self.configfile = configfile

        try:
            from Zope2.Startup.run import configure_wsgi

            configure_wsgi(r"%s" % self.configfile)
        except ImportError:
            try:
                from ZServer.Zope2.Startup.run import configure
            except ImportError:
                try:
                    from Zope2 import configure
                except ImportError:
                    from Zope import configure

            configure(configfile)

        try:
            import Zope2
            app = Zope2.app()
        except ImportError:
            import Zope
            app = Zope.app()

        from Testing.makerequest import makerequest
        self.app = makerequest(app)

        try:
            self._make_permissive()
            print("Permissive security installed")
        except:
            print("Permissive security NOT installed")

        self._pwd = self.portal or self.app

        try:
            from zope.component import getSiteManager
            from zope.component import getGlobalSiteManager
            try:
                from zope.app.component.hooks import setSite
            except ImportError:
                from zope.component.hooks import setSite

            if self.portal is not None:
                setSite(self.portal)

                gsm = getGlobalSiteManager()
                sm = getSiteManager()

                if sm is gsm:
                    print("ERROR SETTING SITE!")
        except:
            # XXX: What exceptions is this supposed to catch?
            pass

    @property
    def utils(self):
        class Utils(object):
            commit = self.commit
            sync = self.sync
            objectInfo = self.objectInfo
            ls = self.ls
            pwd = self.pwd
            cd = self.cd
            su = self.su
            getCatalogInfo = self.getCatalogInfo

            @property
            def cwd(self):
                return self.pwd()

        return Utils()

    @property
    def namespace(self):
        return dict(utils=self.utils, app=self.app, portal=self.portal)

    @property
    def portal(self):
        portals = self.app.objectValues("Plone Site")
        if len(portals):
            return portals[0]
        else:
            return None

    def pwd(self):
        return self._pwd

    def _make_permissive(self):
        """
        Make a permissive security manager with all rights. Hell,
        we're developers, aren't we? Security is for whimps. :)
        """
        from Products.CMFCore.tests.base.security import (
            PermissiveSecurityPolicy)
        import AccessControl
        from AccessControl.SecurityManagement import newSecurityManager
        from AccessControl.SecurityManager import setSecurityPolicy

        _policy = PermissiveSecurityPolicy()
        self.oldpolicy = setSecurityPolicy(_policy)
        newSecurityManager(None, AccessControl.User.system)

    def su(self, username=None):
        """Change to named user. Return to permissive security
        policy if no username is given.
        """
        if username is None:
            self._make_permissive()
            print("PermissiveSecurityPolicy put back in place")
            return

        user = (
            self.portal.acl_users.getUser(username) or
            self.app.acl_users.getUser(username)
        )
        if not user:
            print("Can't find %s in %s" % (username, self.portal.acl_users))
            return

        from AccessControl.ZopeSecurityPolicy import ZopeSecurityPolicy
        from AccessControl.SecurityManagement import newSecurityManager
        from AccessControl.SecurityManagement import getSecurityManager
        from AccessControl.SecurityManager import setSecurityPolicy

        _policy = ZopeSecurityPolicy()
        self.oldpolicy = setSecurityPolicy(_policy)
        wrapped_user = user.__of__(self.portal.acl_users)
        newSecurityManager(None, wrapped_user)
        print('User changed.')
        return getSecurityManager().getUser()

    def getCatalogInfo(self, obj=None, catalog='portal_catalog', query=None,
                       sort_on='created', sort_order='reverse'):
        """ Inspect portal_catalog. Pass an object or object id for a
        default query on that object, or pass an explicit query.
        """
        if obj and query:
            print("Ignoring %s, using query." % obj)

        catalog = self.portal.get(catalog)
        if not catalog:
            return 'No catalog'

        indexes = catalog._catalog.indexes
        if not query:
            if isinstance(obj, six.string_types):
                cwd = self.pwd()
                obj = cwd.unrestrictedTraverse(obj)
            # If the default in the signature is mutable, its value will
            # persist across invocations.
            query = {}
            if indexes.get('path'):
                from string import join
                path = join(obj.getPhysicalPath(), '/')
                query.update({'path': path})
            if indexes.get('getID'):
                query.update({'getID': obj.id, })
            if indexes.get('UID') and shasattr(obj, 'UID'):
                query.update({'UID': obj.UID(), })
        if indexes.get(sort_on):
            query.update({'sort_on': sort_on, 'sort_order': sort_order})
        if not query:
            return 'Empty query'
        results = catalog(**query)

        result_info = []
        for r in results:
            rid = r.getRID()
            if rid:
                result_info.append(
                        {'path': catalog.getpath(rid),
                        'metadata': catalog.getMetadataForRID(rid),
                        'indexes': catalog.getIndexDataForRID(rid), }
                        )
            else:
                result_info.append({'missing': rid})

        if len(result_info) == 1:
            return result_info[0]
        return result_info

    def commit(self):
        """
        Commit the transaction.
        """
        try:
            import transaction
            transaction.get().commit()
        except ImportError:
            get_transaction().commit()

    def sync(self):
        """
        Sync the app's view of the zodb.
        """
        self.app._p_jar.sync()

    def objectInfo(self, o):
        """
        Return a descriptive string of an object
        """
        Title = ""
        t = getattr(o, 'Title', None)
        if t:
            Title = t()
        return {'id': o.getId(),
                'Title': Title,
                'portal_type': getattr(o, 'portal_type', o.meta_type),
                'folderish': o.isPrincipiaFolderish,
                }

    def cd(self, path):
        """
        Change current dir to a specific folder.

         cd( ".." )
         cd( "/plone/Members/admin" )
         cd( portal.Members.admin )
         etc.
        """
        if not isinstance(path, str):
            path = '/'.join(path.getPhysicalPath())
        cwd = self.pwd()
        x = cwd.unrestrictedTraverse(path)
        if x is None:
            raise KeyError("Can't cd to %s" % path)

        print("%s -> %s" % (self.pwd().getId(), x.getId()))
        self._pwd = x

    def ls(self, x=None):
        """
        List object(s)
        """
        if isinstance(x, six.string_types):
            cwd = self.pwd()
            x = cwd.unrestrictedTraverse(x)
        if x is None:
            x = self.pwd()
        if x.isPrincipiaFolderish:
            return [self.objectInfo(o) for id, o in x.objectItems()]
        else:
            return self.objectInfo(x)

zope_debug = None


def ipy_set_trace():
    try:
        from IPython import Debugger
        Debugger.Pdb().set_trace()
    except ImportError:
        # IPython 0.10.2+
        from IPython.core.debugger import Pdb
        Pdb().set_trace()


def main():
    global zope_debug
    ip = get_inst()
    # autocall to "full" mode (smart mode is default, I like full mode)

    SOFTWARE_HOME = os.environ.get("SOFTWARE_HOME")
    if SOFTWARE_HOME:
        sys.path.append(SOFTWARE_HOME)
        print("SOFTWARE_HOME=%s\n" % SOFTWARE_HOME)
    else:
        print("No $SOFTWARE_HOME set, assume Zope >= 2.12 (Plone 4 has this).")

    zope_debug = ZopeDebug()

    # <HACK ALERT>
    import pdb
    pdb.set_trace = ipy_set_trace
    # </HACK ALERT>

    available_utils = ", ".join([
        x for x in
        dir(zope_debug.utils)
        if not x.startswith("_")]
    )
    print(textwrap.dedent("""
        ZOPE mode iPython shell.

          Bound names:
           app
           portal
           utils.{%s}

        If you call utils.su() with no arguments, the PermissiveSecurityPolicy
        will be put back in place.

        """ % available_utils))
    if SOFTWARE_HOME:
        print("Uses the $SOFTWARE_HOME and $CONFIG_FILE environment variables.")
    else:
        print("Uses the $CONFIG_FILE environment variable.")

    ip.user_ns.update(zope_debug.namespace)

# vim: set ft=python ts=4 sw=4 expandtab :
