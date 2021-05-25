# -*- coding: utf-8 -*-

import json
from plone import api
from Products.Five import BrowserView
from zope.interface import implements
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from interfaces import IManageCollections
from connexion_db import ConnexionDb
import mysql.connector


class ManageCollections(ConnexionDb):
    """
    gestion des collectes de saclots de prélèvements
    pa' l' tchauffeu.
    """
    implements(IManageCollections)

    def getAllCollections(self):
        """
        Récupères les collectes de saclots
        table mitsibox_collect_history
        """
        tableCollections = self.getLabDbAccessTable('mitsibox_collect_history')
        recs = tableCollections.select().execute()  # cas d'une table
        myCollections = recs.fetch_all()
        return myCollections


    def getAllSamplesFormBox(self, idBox):
        """
        table mitsibox_samples
        récupères tous le total qui ont été déposés dans une boite
        et dont le statut est INBOX
        """
        collectSamples = self.getLabDbAccessCollection('mitsibox_samples')
        recs = (collectSamples.find(("box_id='%s' and status='INBOX'")%(idBox,)).fields("_id")).execute()
        mySamples = recs.fetch_all()
        return mySamples

    def getCollectionHistoryId(self, idRound):
        """
        table mitsibox_collect_history
        Vérifie si à la date courante il existe déjà une
        instance de la collection
            Si oui retourner l'id ce cette collecte
                (tournée en cours pour ce chauffeur)
            Si non créer une nouvelle instance de collecte
                (une nouvlle tournée pour ce chauffeur)
        """
        drivers = getMultiAdapter((self.context, self.request), name="manageDrivers")

        db = self.getLabDbAccessTable('mitsibox_collect_history')
        request = db.session.sql("""
                                 select
                                     id
                                 from
                                     mitsi_chuhautesenne.mitsibox_collect_history
                                 where
                                     round_id = '%s'
                                     and
                                     status_collect='ACTIVE'
                                     and start_date >= curdate();
                                 """ % (idRound,)).execute()
        result = request.fetch_one()

        if (result is None):
            driverId = api.user.get_current()
            statusCollect = "ACTIVE"
            request = db.session.sql("""
                                       insert into mitsi_chuhautesenne.mitsibox_collect_history
                                          (round_id,
                                           driver_id,
                                           status_collect)
                                       values
                                          ('%s', '%s', '%s')""" % (idRound, driverId, statusCollect)).execute()

            request.get_autoincrement_value()  # recupère la clé qui vient d'être insérée

            lastCollectHistoryId = request.get_autoincrement_value()
            return lastCollectHistoryId
        else:
            lastCollectHistoryId = result["id"]
            return lastCollectHistoryId

    def insertCollectionByDriver(self):
        """
        insertion d'une collecte de saclot pa' l'tchauffeu
        table mitsibox_collect_box_history
        """
        fields = self.request.form
        idBox = fields.get('idBox', None)
        idDriver = fields.get('idDriver', None)
        idRound = fields.get('idRound', None)
        totalSamplesCollect = fields.get('totalSaclots', None)
        collectBoxDriverComment = fields.get('collectBoxDriverComment', None)
        statusCollect = "INBOX"

        mySamples = self.getAllSamplesFormBox(idBox)
        print "===> MYSAMPLES : %s" % (mySamples,)

        collectHistoryId = self.getCollectionHistoryId(idRound)

        # ouverture de la connexion
        session = self.getConnexion()
        #  db = session.get_schema("mitsi_chuhautesenne")

        # recup du dernier _id qui vient d'être inséré
        # request = session.sql("select last_insert_id()").execute()
        # collect_history_id = request.fetch_one()[0]
        # print "collect_history_id : %s" % (collect_history_id,)
        # print "box_id : %s" % (box_id,)

        # Insertion dans la table tableCollectBoxHistory
        # lorsqu'un chauffeur recupère les saclots d'une boite
        tableCollectBoxHistory = self.getLabDbAccessTable('mitsibox_collect_box_history')
        tableCollectBoxHistory.insert(['collect_history_id', 'box_id', 'collect_box_driver_comment', 'collect_box_driver_samples_total']).values(collectHistoryId, idBox, collectBoxDriverComment, int(totalSamplesCollect)).execute()
        session.commit()

        portalUrl = getToolByName(self.context, 'portal_url')()
        ploneUtils = getToolByName(self.context, 'plone_utils')
        message = u"La collecte est enregistrée."
        ploneUtils.addPortalMessage(message, 'info')
        url = "%s/driver-form" % (portalUrl,)
        self.request.response.redirect(url)
        return ''

    def updateCollection(self):
        """
        update des données d'une collecte de saclots pa' l' tchauffeu
        table mitsibox_collect_history
        """
        tableCollections = self.getLabDbAccessTable('mitsibox_collect_history')

        fields = self.request.form
        idCollection = fields.get('idCollection', None)

        myCollection = {}
        myCollection['lastName'] = fields.get('driverLastName', None).decode('utf-8')
        myCollection['firstName'] = fields.get('driverFirstName', None).decode('utf-8')
        myCollection['gsm'] = fields.get('driverGsm', None)

        tableCollections.modify("_id='%s'" % idCollection).patch(myCollection).execute()

        portalUrl = getToolByName(self.context, 'portal_url')()
        ploneUtils = getToolByName(self.context, 'plone_utils')
        message = u"les données de la collecte ont été modifiées."
        ploneUtils.addPortalMessage(message, 'info')
        url = "%s/collecte-des-boites" % (portalUrl,)
        self.request.response.redirect(url)
        return ''

    def insertSamples(self, idBox, status):
        """
        /!\ ne sert que pour les RFID
        ajouter chaque sample prélevé dans une boite
        dans la table mitsibox_sample_events avec son statut à TRANSIT
        table mitsibox_sample_events
        """
        collectionsSample = self.getLabDbAccessTable('mitsibox_sample_events')

        mySamples = self.getAllSamplesFormBox(idBox)
        for i in range(len(mySamples)):
            collectionsSample.insert(['sample_id', 'box_id', 'status']).values(mySamples[i]['_id'], idBox, status).execute()

    def updateStatusSamples(self, idBox, status):
        """
        /!\ ne sert que pour les RFID
        table mitsibox_samples
        mettre à jour les samples d'une box au moment
        où ils sont
            - prélevés par le driver     ==> TRANSIT
            - réceptionnés par le labo   ==> LABO
        Satut INBOX TRANSIT LABO
        """
        collectSamples = self.getLabDbAccessCollection('mitsibox_samples')
        request = collectSamples.modify((("box_id='%s' and status='TRANSIT'") % (idBox,))).set("status", "%s" % (status,)).execute()

    def receptionCollectByLabo(self):
        """
        table mitsibox_collect_history
        Mise a jour des données d'une collect lorsque le driver arrive au labo.
        L'employé encode le nombre de prélèvement ramené par le chauffeur†
        La end_date est insrée (moment de la fin de la collecte)
        Le status_collect passe à DONE (fin e la collecte)
        """
        fields = self.request.form
        idRound = fields.get('idRound', None)

        collectHistoryId = self.getCollectionHistoryId(idRound)
        print "===> MYCOLLECTID : %s" % (collectHistoryId,)

        myCollection = {}
        myCollection['status_collect'] = "DONE"
        myCollection['employe_id'] = fields.get('idEmployeLab', None)
        myCollection['labo_comment'] = fields.get('commentairEmploye', None)
        myCollection['samples_total_labo'] = fields.get('totalSaclots', None) or 0

        tableCollectHistory = self.getLabDbAccessTable('mitsibox_collect_history')

        # XXXXXXXXXXXXXXXXXXXX
        tableCollectHistory.update(("_id='%s'" % collectHistoryId).set(myCollection)).execute()

        portalUrl = getToolByName(self.context, 'portal_url')()
        ploneUtils = getToolByName(self.context, 'plone_utils')
        message = u"La collecte est enregistrée."
        ploneUtils.addPortalMessage(message, 'info')
        url = "%s/reception-dune-tournee" % (portalUrl,)
        self.request.response.redirect(url)
        return ''








































