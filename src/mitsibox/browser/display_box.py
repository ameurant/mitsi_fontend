# -*- coding: utf-8 -*-

import json
# import mysqlx
from plone import api
from Products.Five import BrowserView
from zope.interface import implements
from interfaces import IManageDisplayBox
from connexion_db import ConnexionDb


class DisplayBox(ConnexionDb):
    """
    recupère toutes les news et les renvoie en JSON
    """
    implements(IManageDisplayBox)

    def getJsonBox(self):
        """
        récupère les paramètres des boites au format JSON
        """
        tablesBoxes = self.getLabDbAccessCollection('mitsibox_boxes')
        recs = tablesBoxes.find().execute()
        myBoxes = recs.fetch_all()
        idList = []
        for el in myBoxes:
            idList.append(dict(el))
        myBoxes = json.dumps(idList)
        return myBoxes

    def splitStatusBatteryBox(self, statutBattery):
        """
        récupère le statut de la batterie
        """
        infoBattery = statutBattery.split(' ')
        return infoBattery

    def getListingAllBoxes(self):
        """
        Récupères les infos de toutes les boites
        """
        tablesBoxes = self.getLabDbAccessCollection('mitsibox_boxes')
        #recs = tablesBoxes.find("lab_id=='%s'"%(idLab,)).execute()
        recs = tablesBoxes.find().execute()
        myBoxes = recs.fetch_all()
        return myBoxes

    def getListingBoxesOnProduction(self):
        """
        Récupères les infos de toutes les boites
        en production productionsstate = True
        """
        collectionBoxes = self.getLabDbAccessCollection('mitsibox_boxes')
        recs = collectionBoxes.find("productionstate='True'").execute()
        myBoxes = recs.fetch_all()
        print("===> myBoxes : %s") % (myBoxes,)
        return myBoxes

    def getOneBox(self, idBox):
        """
        Récupères les infos d'une boite selon son tidentifiant
        """
        tablesBoxes = self.getLabDbAccessCollection('mitsibox_boxes')
        recs = tablesBoxes.find("_id=='%s'" % (idBox,)).execute()
        myBoxe = recs.fetch_one()
        return myBoxe
