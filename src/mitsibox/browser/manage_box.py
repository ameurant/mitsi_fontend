# -*- coding: utf-8 -*-

import json
from plone import api
from Products.Five import BrowserView
from zope.interface import implements
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from interfaces import IManageBox
from connexion_db import ConnexionDb


class ManageBox(ConnexionDb):
    """
    gestion des boites
    """
    implements(IManageBox)

    def getListingAllBoxes(self):
        """
        Récupères les infos de toutes les boites
        """
        tablesBoxes = self.getLabDbAccessCollection('mitsibox_boxes')
        recs = tablesBoxes.find().execute()
        # recs = tbl_mitsibox.select().execute()
        myBoxes = recs.fetch_all()
        return myBoxes

    def getOneBoxById(self, idBox):
        """
        Récupères les infos d'une boite selon son identifiant
        """
        tablesBoxes = self.getLabDbAccessCollection('mitsibox_boxes')
        recs = tablesBoxes.find("_id=='%s'" % (idBox,)).execute()
        myBox = recs.fetch_one()
        return myBox

    def getAllBoxesFromRound(self, idRound):
        """
        Récupère toues les infos des boites d'une tournée mitsibox_boxes
        """
        roundsTools = getMultiAdapter((self.context, self.request), name="manageRounds")
        boxList = roundsTools.getRoundById(idRound)
        idBoxList = boxList['roundMitsiboxList']
        filtre = "_id in {0}".format(list(i.encode() for i in idBoxList))

        tablesBoxes = self.getLabDbAccessCollection('mitsibox_boxes')
        recs = tablesBoxes.find(filtre).fields('_id', 'name', 'address', 'cp', 'localite', 'lat', 'long', 'deposit_count').execute()
        allBoxes = recs.fetch_all()
        return allBoxes

    def getJsonOfAllBoxesFromRound(self, idRound):
        """
        Récupère toues les infos des boites d'une tournée
        """
        roundsTools = getMultiAdapter((self.context, self.request), name="manageRounds")
        boxList = roundsTools.getRoundById(idRound)
        idBoxList = boxList['roundMitsiboxList']
        filtre = "_id in {0}".format(list(i.encode() for i in idBoxList))

        tablesBoxes = self.getLabDbAccessCollection('mitsibox_boxes')
        recs = tablesBoxes.find(filtre).fields('name', 'address', 'cp', 'localite', 'lat', 'long', 'deposit_count').execute()

        allBoxesList = []
        for el in recs.fetch_all():
            allBoxesList.append(dict(el))
        allBoxesJson = json.dumps(allBoxesList)
        return allBoxesJson

    def insertBox(self):
        """
        insertion d'une nouvelle boite
        """
        tablesBoxes = self.getLabDbAccessCollection('mitsibox_boxes')

        fields = self.request.form

        newBox = {}
        newBox['lab_id'] = fields.get('laboId', None)
        newBox['name'] = fields.get('boxName', None).decode("utf-8")
        newBox['address'] = fields.get('boxAddress', None).decode("utf-8")
        newBox['cp'] = fields.get('boxCp', None)
        newBox['localite'] = fields.get('boxLocalite', None).decode("utf-8")
        newBox['lat'] = fields.get('boxLat', None)
        newBox['long'] = fields.get('boxLong', None)
        newBox['ssid'] = fields.get('boxSsidWifi', None)
        newBox['passwifi'] = fields.get('boxPassWifi', None)
        newBox['cardSimId'] = fields.get('boxCarteSimId', None)
        newBox['cardSimPuk'] = fields.get('boxCarteSimPuk', None)
        newBox['cardPhoneNumber'] = fields.get('boxNumeroTelephone', None)
        newBox['alertsms'] = fields.get('boxAlertSms', None)
        newBox['arduino'] = fields.get('boxArduino', None)
        newBox['productionstate'] = fields.get('boxProductionState', None)

        tablesBoxes.add(newBox).execute()

        portalUrl = getToolByName(self.context, 'portal_url')()
        ploneUtils = getToolByName(self.context, 'plone_utils')
        message = u"Ok les données de la boite ont été enregistrées."
        ploneUtils.addPortalMessage(message, 'info')
        url = "%s/gestion-des-boites/listing-des-mitsibox" % (portalUrl,)
        self.request.response.redirect(url)
        return ''

    def updateBox(self):
        """
        insertion d'une nouvelle boite
        """
        tablesBoxes = self.getLabDbAccessCollection('mitsibox_boxes')

        fields = self.request.form
        idBox = fields.get('idBox', None)

        myBox = {}
        myBox['lab_id'] = fields.get('laboId', None)
        myBox['name'] = fields.get('boxName', None).decode("utf-8")
        myBox['address'] = fields.get('boxAddress', None).decode("utf-8")
        myBox['cp'] = fields.get('boxCp', None)
        myBox['localite'] = fields.get('boxLocalite', None).decode("utf-8")
        myBox['lat'] = fields.get('boxLat', None)
        myBox['long'] = fields.get('boxLong', None)
        myBox['ssid'] = fields.get('boxSsidWifi', None)
        myBox['passwifi'] = fields.get('boxPassWifi', None)
        myBox['cardSimId'] = fields.get('boxCarteSimId', None)
        myBox['cardSimPuk'] = fields.get('boxCarteSimPuk', None)
        myBox['cardPhoneNumber'] = fields.get('boxNumeroTelephone', None)
        myBox['alertsms'] = fields.get('boxAlertSms', None)
        myBox['arduino'] = fields.get('boxArduino', None)
        myBox['productionstate'] = fields.get('boxProductionState', None)

        tablesBoxes.modify("_id='%s'" % idBox).patch(myBox).execute()

        portalUrl = getToolByName(self.context, 'portal_url')()
        ploneUtils = getToolByName(self.context, 'plone_utils')
        message = u"Ok les données de cette boite ont été modifiées."
        ploneUtils.addPortalMessage(message, 'info')
        url = "%s/gestion-des-boites/listing-des-mitsibox" % (portalUrl,)
        self.request.response.redirect(url)
        return ''
