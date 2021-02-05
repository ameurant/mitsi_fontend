# -*- coding: utf-8 -*-

import mysqlx
from Products.Five import BrowserView

LABNAME = "mitsi_chuhautesenne"

class ConnexionDb(BrowserView):
    """
    connexion sur la db mitsibox
    """

    def getConnexion(self):
        """
        crée une connexion sur la db
        en local 44060
        sur becker 33060
        """
        session = mysqlx.get_session({
                    'host': '127.0.0.1', 
                    'port': 33060,
                    'user': 'mitsibox',
                    'password': '69AlainAvouluJouer$',
                    'ssl-mode': 'DISABLED'
                })

        return session

    def getLabDbAccess(self):
        """
        recupère la db d'un schema de laboratoire
        """
        session = self.getConnexion()
        db = session.get_schema(LABNAME)
        return db

    def getLabDbAccessCollection(self, collectionName):
        """
        recupère les collections d'un schema de laboratoire
        """
        session = self.getConnexion()
        db = session.get_schema(LABNAME)
        collectionMitsibox = db.get_collection(collectionName)
        return collectionMitsibox

    def getLabDbAccessTable(self, tableName):
        """
        recupère la table d'un schema de laboratoire
        """
        session = self.getConnexion()
        db = session.get_schema(LABNAME)
        tableMitsibox = db.get_table(tableName)
        return tableMitsibox
