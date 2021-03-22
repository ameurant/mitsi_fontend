# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IMitsiboxCoreLayer(IDefaultBrowserLayer):
    """
    Layer for all box developments
    """


class IManageCommon(Interface):
    """
    IManageCommon
    """


class IshowBox(Interface):
    """
    IshowBox
    """


class IManageConnexionDb(Interface):
    """
    IManageConnexionDb
    """


class IManageLabs(Interface):
    """
    IManageLabs
    """


class IManageBox(Interface):
    """
    IManageBox
    """


class IManageDisplayBox(Interface):
    """
    IManageDisplayBox
    """


class IManageDrivers(Interface):
    """
    IManageDrivers
    """


class IManageFleetManagers(Interface):
    """
    IManageFleetManagers
    """


class IManageRounds(Interface):
    """
    IManageRounds
    """

class IManageCollections(Interface):
    """
    IManageCollections
    """
