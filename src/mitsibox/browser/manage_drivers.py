# -*- coding: utf-8 -*-

# import json
# from plone import api
# from Products.Five import BrowserView
from zope.interface import implements
# from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from interfaces import IManageDrivers
from connexion_db import ConnexionDb


class ManageDrivers(ConnexionDb):
    """
    gestion des boites
    """
    implements(IManageDrivers)

    def getAllDrivers(self):
        """
        Récupères les infos de toutes les chauffeurs
        """
        tablesDrivers = self.getLabDbAccessCollection('mitsibox_drivers')
        recs = tablesDrivers.find().execute()
        # recs = tbl_mitsibox.select().execute()
        myDrivers = recs.fetch_all()

        return myDrivers

    def getDriverById(self, idDriver):
        """
        Récupères les infos d'un chauffeur selon son ID
        """
        tablesDrivers = self.getLabDbAccessCollection('mitsibox_drivers')
        recs = tablesDrivers.find("_id=='%s'" % (idDriver,)).execute()
        myDriver = recs.fetch_one()
        return myDriver

    def getIdDriverByIdRound(self, idRound):
        """
        Récupères les infos d'un chauffeur selon l'id d'une trounée
        """
        tablesRounds = self.getLabDbAccessCollection('mitsibox_rounds')
        recs = tablesRounds.find("roundDriverId=='%s'" % (idRound,)).execute()
        myDriver = recs.fetch_one()
        return myDriver

    def getDriverIdByLoginPlone(self, loginPlone):
        """
        Récupères les infos d'un chauffeur selon son ID dans Plone
        """
        if (loginPlone == 'admin'):
            tablesDrivers = self.getLabDbAccessCollection('mitsibox_drivers')
            recs = tablesDrivers.find("idDriver=='%s'" % (loginPlone,)).execute()
            myDriver = recs.fetch_one()
        else:
            myDriver = loginPlone
        return myDriver

    def createDriver(self, driverId, driverEmail, driverFullname, passDriver):
        """
        créer un driver dans le plone portal_membership
        """
        registration = getToolByName(self.context, 'portal_registration')
        membership = getToolByName(self.context, 'portal_membership')
        acl_users = getToolByName(self.context, 'acl_users')

        # password = ''.join(random.choice(chars) for char in range(8))
        properties = {
            'username': driverId,
            'email': driverEmail,
            'fullname': driverFullname.encode('utf-8')
        }
        registration.addMember(driverId, passDriver, properties=properties)
        acl_users.updateLoginName(driverId, driverEmail)

        self.addDriverToGroupDrivers(driverId)

        return membership.getMemberById(driverId)

    def addDriverToGroupDrivers(self, driverId):
        """
        ajouter un driver dans le plone group drivers
        """
        portal_groups = getToolByName(self.context, 'portal_groups')
        portal_groups.addPrincipalToGroup(driverId, 'drivers')

    def insertDriver(self):
        """
        insertion d'une nouvelle drivers
        """
        tablesDrivers = self.getLabDbAccessCollection('mitsibox_drivers')

        fields = self.request.form

        lastName = fields.get('driverLastName', None).decode('utf-8')
        firstName = fields.get('driverFirstName', None).decode('utf-8')
        driverId = fields.get('driverId', None)
        driverPass = fields.get('driverPass', None)
        driverFullName = firstName + u" " + lastName
        driverSmsNotification = fields.get('driverSmsNotification', None)
        driverEmail = 'alain.meurant@skynet.be'

        newDriver = {}
        newDriver['lastName'] = lastName
        newDriver['firstName'] = firstName
        newDriver['gsm'] = fields.get('driverGsm', None)
        newDriver['driverSmsNotification'] = driverSmsNotification
        newDriver['idDriver'] = driverId
        newDriver['passDriver'] = driverPass

        tablesDrivers.add(newDriver).execute()

        self.createDriver(driverId, driverEmail, driverFullName, driverPass)

        portalUrl = getToolByName(self.context, 'portal_url')()
        ploneUtils = getToolByName(self.context, 'plone_utils')
        message = u"Le chauffeur est enregistrée."
        ploneUtils.addPortalMessage(message, 'info')
        url = "%s/gestion-des-chauffeurs/listing-des-chauffeurs" % (portalUrl,)
        self.request.response.redirect(url)
        return ''

    def updateDriver(self):
        """
        insertion d'une nouvelle boite
        """
        tablesDrivers = self.getLabDbAccessCollection('mitsibox_drivers')

        fields = self.request.form
        idDriver = fields.get('idDriver', None)

        myDriver = {}
        myDriver['lastName'] = fields.get('driverLastName', None).decode('utf-8')
        myDriver['firstName'] = fields.get('driverFirstName', None).decode('utf-8')
        myDriver['gsm'] = fields.get('driverGsm', None)
        myDriver['idDriver'] = fields.get('driverId', None)
        myDriver['driverSmsNotification'] = fields.get('driverSmsNotification', None)
        myDriver['passDriver'] = fields.get('driverPass', None)

        tablesDrivers.modify("_id='%s'" % idDriver).patch(myDriver).execute()

        portalUrl = getToolByName(self.context, 'portal_url')()
        ploneUtils = getToolByName(self.context, 'plone_utils')
        message = u"les données du chauffeur ont été modifiées."
        ploneUtils.addPortalMessage(message, 'info')
        url = "%s/gestion-des-chauffeurs/listing-des-chauffeurs" % (portalUrl,)
        self.request.response.redirect(url)
        return ''
