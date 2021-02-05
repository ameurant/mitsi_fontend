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

    def getAllSamplesFormBox(self, boxId):
        """
        table mitsibox_samples
        récupères tous les samples qui ont été déposés dans uen boite
        et dont le statut est INBOX
        """
        collectSamples = self.getLabDbAccessCollection('mitsibox_samples')
        recs = (collectSamples.find(("box_id='%s' and status='INBOX'")%(boxId,)).fields("_id")).execute()
        mySamples = recs.fetch_all()
        return mySamples

    def getCollectionId(self, roundId):
        """
        table mitsibox_collect_history
        Vérifie si à la date courante il existe déjà une
        instance de la collection
            Si oui retourner l'id
            Si non créer l'instance de la collection
        """
        drivers = getMultiAdapter((self.context, self.request), name="manageDrivers")
        
        db = self.getLabDbAccess()
        request = db.session.sql("""
                                 select
                                     id
                                 from
                                     mitsi_chuhautesenne.mitsibox_collect_history
                                 where
                                     round_id = '00005ecb95df0000000000000010'
                                     and
                                     status='ACTIVE'
                                     and start_date >= curdate();
                                 """).execute()
        result = request.fetch_one()
        print "result : %s" % (result,)

        if (result is None):
            "inserer le round_id, le driver_id status a ACTIVE"
            round_id = roundId
            driver_id = drivers.getIdDriverByIdRound(roundId)
            print ("driverId : %s") % (driver_id,)
            status = "ACTIVE"
            request = db.session.sql("""
                                     insert into mitsi_chuhautesenne.mitsibox_collect_history
                                        (round_id,
                                        driver_id,
                                        status)
                                     values
                                        (%s, %s, %s)""" % (round_id, driver_id, status)).execute()
            request = session.sql("select last_insert_id()").execute()
            collectHistoryId = request.fetch_one()[0]
            print "getCollectionId"
            print "collectHistoryId : %s" % (collectHistoryId,)
            return collectHistoryId
        else:
            print "getCollectionId"
            print "collectHistoryId : %s" % (result.id,)
            return result.id

    def insertCollectionByDriver(self):
        """
        insertion d'une collecte de saclot pa' l'tchauffeu
        table mitsibox_collect_box_history
        """
        fields = self.request.form
        boxId = fields.get('boxId', None)
        roundId = fields.get('boxId', None)
        samplesTotal = fields.get('totalSaclots', None)
        collectBoxComment = fields.get('collectBoxComment', None)
        status = "INBOX"
        boxId = "00005f0d88fe0000000000000018"

        mySamples = self.getAllSamplesFormBox(boxId)
        print "mySamples : %s" % (mySamples,)
        # print "mySamples Id : %s" % (mySamples[0]['_id'],)

        collectHistoryId = self.getCollectionId(roundId)
        print "collectHistoryId : %s" % (collectHistoryId,)

        #self.updateStatusSamples(boxId, status)
        #self.insertSamples(boxId, status)


        #self.getCollectionId(roundId)



        # ouverture de la connexion
        session = self.getConnexion()
        db = session.get_schema("mitsi_chuhautesenne")

        # recupe des deux tables
        tableCollectHistory = db.get_table('mitsibox_collect_history')
        tableCollectBoxHistory = db.get_table('mitsibox_collect_box_history')

        # Insertion dans la table tableCollectHistory
        # tableCollectHistory = self.getLabDbAccessTable('mitsibox_collect_history')
        #tableCollectHistory.insert(['round_id', 'driver_id', 'box_id', 'samples_total', 'collect_comment', 'status']).values(round_id, driver_id, box_id, samples_total, collect_comment, status).execute()
        #session.commit()

        # recup du dernier _id qui vient d'être inséré
        #request = session.sql("select last_insert_id()").execute()
        #collect_history_id = request.fetch_one()[0]
        #print "collect_history_id : %s" % (collect_history_id,)
        #print "box_id : %s" % (box_id,)

        # Insertion dans la table tableCollectBoxHistory
        # tableCollectBoxHistory = self.getLabDbAccessTable('mitsibox_collect_box_history')
        #tableCollectBoxHistory.insert(['collect_history_id', 'box_id', 'collect_box_comment']).values(collect_history_id, box_id, collect_box_comment).execute()
        #session.commit()

        portalUrl = getToolByName(self.context, 'portal_url')()
        ploneUtils = getToolByName(self.context, 'plone_utils')
        message = u"La collecte est enregistrée."
        ploneUtils.addPortalMessage(message, 'info')
        url = "%s/collecte-des-boites" % (portalUrl,)
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
 
    def insertSamples(self, boxId, status):
        """
        ajouter chaque sample prélever dans une boite 
        dans la table mitsibox_sample_events avec son statut à TRANSIT
        table mitsibox_sample_events
        """
        collectionsSample = self.getLabDbAccessTable('mitsibox_sample_events')

        mySamples = self.getAllSamplesFormBox(boxId)
        for i in range(len(mySamples)):
            collectionsSample.insert(['sample_id', 'box_id', 'status']).values(mySamples[i]['_id'], boxId, status).execute()


    def updateStatusSamples(self, boxId, status):
        """
        table mitsibox_samples
        mettre à jour les samples d'une box au moment
        où ils sont prélevés par le driver
        Satut INBOX TRANSIT PENDING LABO
        """
        collectSamples = self.getLabDbAccessCollection('mitsibox_samples')
        request = collectSamples.modify((("box_id='%s' and status='TRANSIT'") % (boxId,))).set("status", "%s" % (status,)).execute()

        








































