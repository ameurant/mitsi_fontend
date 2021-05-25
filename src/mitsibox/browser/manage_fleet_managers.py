# -*- coding: utf-8 -*-

# import json
# from plone import api
# from Products.Five import BrowserView
from zope.interface import implements
# from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from interfaces import IManageFleetManagers
from connexion_db import ConnexionDb


class ManageFleetManagers(ConnexionDb):
    """
    gestion des manager des flottes qui doivent
    recevoir une notification SMS lors du premier dépot
    d'un prélèvement après qu'une boite soit vide
    """
    implements(IManageFleetManagers)

    def getAllFleetManagers(self):
        """
        Récupères les infos de toutes fleet managers
        """
        tableFleetManagers = self.getLabDbAccessCollection('mitsibox_fleet_managers')
        recs = tableFleetManagers.find().execute()
        # recs = tbl_mitsibox.select().execute()
        myFleetManagers = recs.fetch_all()

        return myFleetManagers

    def getFleetManagerById(self, fleetManagerId):
        """
        Récupères les infos d'un fleet-manager selon son ID
        """
        tableFleetManagers = self.getLabDbAccessCollection('mitsibox_fleet_managers')
        recs = tableFleetManagers.find("_id=='%s'" % (fleetManagerId,)).execute()
        myFleetManager = recs.fetch_one()

        return myFleetManager

    def getFleetManagerIdByLoginPlone(self, loginPlone):
        """
        Récupères les infos d'un fleet-manager selon son ID dans Plone
        """
        if (loginPlone == 'admin'):
            tableFleetManagers = self.getLabDbAccessCollection('mitsibox_fleet_managers')
            recs = tableFleetManagers.find("idFleetManager=='%s'" % (loginPlone,)).execute()
            myFleetManager = recs.fetch_one()
        else:
            myFleetManager = loginPlone
        return myFleetManager

    def createFleetManager(self, fleetManagerlastName, fleetManagerfirstName, fleetManagerEmail, fleetManagerIdPlone, fleetManagerPassPlone):
        """
        créer un fleetManager dans le plone portal_membership
        """
        registration = getToolByName(self.context, 'portal_registration')
        membership = getToolByName(self.context, 'portal_membership')
        acl_users = getToolByName(self.context, 'acl_users')

        fleetManagerFullname = fleetManagerfirstName + ' ' + fleetManagerlastName

        # password = ''.join(random.choice(chars) for char in range(8))
        properties = {
            'username': fleetManagerIdPlone,
            'email': fleetManagerEmail,
            'fullname': fleetManagerFullname.encode('utf-8')
        }
        registration.addMember(fleetManagerIdPlone, fleetManagerPassPlone, properties=properties)
        acl_users.updateLoginName(fleetManagerIdPlone, fleetManagerEmail)
        return membership.getMemberById(fleetManagerIdPlone)

    def insertFleetManager(self):
        """
        insertion d'un nouveau fleet-manager
        """
        tableFleetManagers = self.getLabDbAccessCollection('mitsibox_fleet_managers')

        fields = self.request.form

        fleetManagerlastName = fields.get('fleetManagerLastName', None).decode('utf-8')
        fleetManagerfirstName = fields.get('fleetManagerFirstName', None).decode('utf-8')
        fleetManagerIdPlone = fields.get('fleetManagerIdPlone', None)
        fleetManagerPassPlone = fields.get('fleetManagerPassPlone', None)
        fleetManagerSmsNotification = fields.get('fleetManagerSmsNotification', None)
        fleetManagerGsm = fields.get('fleetManagerGsm', None)
        fleetManagerEmail = fields.get('fleetManagerEmail', None)

        newFleetManager = {}
        newFleetManager['fleetManagerLastName'] = fleetManagerlastName
        newFleetManager['fleetManagerFirstName'] = fleetManagerfirstName
        newFleetManager['fleetManagerEmail'] = fleetManagerEmail
        newFleetManager['fleetManagerGsm'] = fleetManagerGsm
        newFleetManager['fleetManagerSmsNotification'] = fleetManagerSmsNotification
        newFleetManager['fleetManagerIdPlone'] = fleetManagerIdPlone
        newFleetManager['fleetManagerPassPlone'] = fleetManagerPassPlone

        tableFleetManagers.add(newFleetManager).execute()

        # ajouter le fleet-manager dans control-panle de plone
        self.createFleetManager(fleetManagerlastName, fleetManagerfirstName, fleetManagerEmail, fleetManagerIdPlone, fleetManagerPassPlone)

        portalUrl = getToolByName(self.context, 'portal_url')()
        ploneUtils = getToolByName(self.context, 'plone_utils')
        message = u"Le fleet manager est enregistré."
        ploneUtils.addPortalMessage(message, 'info')
        url = "%s/administration-de-la-db/gestion-des-fleet-managers/listing-des-fleet-managers" % (portalUrl,)
        self.request.response.redirect(url)
        return ''

    def updateFleetManager(self):
        """
        Mise à jour des information d'un fleet-manager
        """
        tableFleetManagers = self.getLabDbAccessCollection('mitsibox_fleet_managers')

        fields = self.request.form
        fleetManagerId = fields.get('fleetManagerId', None)

        myFleetManager = {}
        myFleetManager['fleetManagerLastName'] = fields.get('fleetManagerLastName', None).decode('utf-8')
        myFleetManager['fleetManagerFirstName'] = fields.get('fleetManagerFirstName', None).decode('utf-8')
        myFleetManager['fleetManagerEmail'] = fields.get('fleetManagerEmail', None)
        myFleetManager['fleetManagerGsm'] = fields.get('fleetManagerGsm', None)
        myFleetManager['fleetManagerSmsNotification'] = fields.get('fleetManagerSmsNotification', None)
        myFleetManager['fleetManagerIdPlone'] = fields.get('fleetManagerIdPlone', None)
        myFleetManager['fleetManagerPassPlone'] = fields.get('fleetManagerPassPlone', None)

        tableFleetManagers.modify("_id='%s'" % fleetManagerId).patch(myFleetManager).execute()

        portalUrl = getToolByName(self.context, 'portal_url')()
        ploneUtils = getToolByName(self.context, 'plone_utils')
        message = u"les données du fleet manager ont été modifiées."
        ploneUtils.addPortalMessage(message, 'info')
        url = "%s/administration-de-la-db/gestion-des-fleet-managers/listing-des-fleet-managers" % (portalUrl,)
        self.request.response.redirect(url)
        return ''
