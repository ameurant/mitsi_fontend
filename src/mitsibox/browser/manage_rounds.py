# -*- coding: utf-8 -*-

import json
from plone import api
from Products.Five import BrowserView
from zope.interface import implements
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from interfaces import IManageRounds
from connexion_db import ConnexionDb


class ManageRounds(ConnexionDb):
    """
    gestion des tournées
    """
    implements(IManageRounds)

    def getAllRounds(self):
        """
        Récupère les infos de toutes les tournées
        """
        tablesRounds = self.getLabDbAccessCollection('mitsibox_rounds')
        recs = tablesRounds.find().execute()
        myRounds = recs.fetch_all()
        return myRounds

    def getRoundById(self, idRound):
        """
        Récupère les infos d'une tournée selon son _id
        """
        tablesRounds = self.getLabDbAccessCollection('mitsibox_rounds')
        recs = tablesRounds.find("_id =='%s'"%(idRound,)).execute()
        myRound = recs.fetch_one()
        return myRound

    def getRoundByDriverId(self, idDriver):
        """
        Récupère les infos d'une tournée selon l'id du driver
        """
        tablesRounds = self.getLabDbAccessCollection('mitsibox_rounds')
        recs = tablesRounds.find("roundDriverId =='%s'"%(idDriver,)).execute()
        myRound = recs.fetch_one()
        return myRound

    def getRoundsOfBox(self, idBox):
        """
        Récupère le nom dde la tournée à la quelle appartient une box
        """
        session = self.getConnexion()
        db = session.get_schema('mitsi_chuhautesenne')
        request = db.session.sql("""select
                                        doc->>"$._id",
                                        doc->>"$.roundName"
                                    from
                                        mitsi_chuhautesenne.mitsibox_rounds
                                    where
                                        "%s" member of (doc->>'$.roundMitsiboxList')""" % (idBox,)).execute()
        result = request.fetch_one()
        if (result is not None):
            myRound = {}
            (myRound['idRound'], myRound['roundName']) = result
            return myRound
        else:
            return None


    def getDistanceRound(self, idRound):
        """
        Calcule la distance d'une tournée
        """
        #print "idRound : %s" % (idRound,)
        session = self.getConnexion()
        db = session.get_schema('mitsi_chuhautesenne')
        request = session.sql("select sum(distance) as 'round distance' from (select ST_Distance(geo_point, lag(geo_point) OVER w, 'kilometre') as 'distance' from mitsi_chuhautesenne.mitsibox_boxes where _id IN ('{}') window w as (ORDER BY FIELD(_id,'{}'))) as d".format("','".join(db.get_collection('mitsibox_rounds').find("_id='%s'" % (idRound)).fields("roundMitsiboxList").execute().fetch_one()['roundMitsiboxList']), "','".join(db.get_collection('mitsibox_rounds').find("_id='%s'" % (idRound)).fields("roundMitsiboxList").execute().fetch_one()['roundMitsiboxList'])))
        res = request.execute()
        myDistance = res.fetch_one()[0][0]
        return round(myDistance, 2)

    def insertRound(self):
        """
        insertion d'une nouvelle tournée
        """
        tableRounds = self.getLabDbAccessCollection('mitsibox_rounds')
        fields = self.request.form

        newRound = {}
        newRound['roundName'] = fields.get('roundName', None).decode("utf-8")
        newRound['roundType'] = fields.get('roundType', None)
        newRound['roundStartTime'] = fields.get('roundStartTime', None)
        newRound['roundEstimedTime'] = fields.get('roundEstimedTime', None)
        newRound['roundMitsiboxList'] = fields.get('roundMitsiboxList', None)
        newRound['roundDriverId'] = fields.get('roundDriverId', None)

        tableRounds.add(newRound).execute()

        portalUrl = getToolByName(self.context, 'portal_url')()
        ploneUtils = getToolByName(self.context, 'plone_utils')
        message = u"La tounrée est enregistrée."
        ploneUtils.addPortalMessage(message, 'info')
        url = "%s/gestion-des-tournees/listing-des-tournees" % (portalUrl,)
        self.request.response.redirect(url)
        return ''

    def updateRound(self):
        """
        modification d'une tournée
        """
        tablesRounds = self.getLabDbAccessCollection('mitsibox_rounds')
        fields = self.request.form
        idRound = fields.get('idRound', None)

        newRound = {}
        newRound['roundName'] = fields.get('roundName', None).decode("utf-8")
        newRound['roundType'] = fields.get('roundType', None)
        newRound['roundStartTime'] = fields.get('roundStartTime', None)
        newRound['roundEstimedTime'] = fields.get('roundEstimedTime', None)
        newRound['roundMitsiboxList'] = fields.get('roundMitsiboxList', None)
        newRound['roundDriverId'] = fields.get('roundDriverId', None)

        tablesRounds.modify("_id='%s'" % idRound).patch(newRound).execute()

        portalUrl = getToolByName(self.context, 'portal_url')()
        ploneUtils = getToolByName(self.context, 'plone_utils')
        message = u"Les données de la tounrée ont été modifiées."
        ploneUtils.addPortalMessage(message, 'info')
        url = "%s/gestion-des-tournees/listing-des-tournees" % (portalUrl,)
        self.request.response.redirect(url)
        return ''
