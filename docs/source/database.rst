.. _database:

database
========
.. currentmodule:: cdms2.database

.. autosummary::
   :toctree: generated/

      AbstractDatabase
      AbstractDatabase.connect
      AbstractDatabase.loadString
      AbstractDatabase.close
      AbstractDatabase.cachecdml
      AbstractDatabase.getDataset
      AbstractDatabase.getObjFromDataset
      AbstractDatabase.openDataset
      AbstractDatabase.searchFilter
      AbstractDatabase.enableCache
      AbstractDatabase.disableCache
      AbstractDatabase.useRequestManager
      AbstractDatabase.usingRequestManager
      AbstractDatabase.repr
      
      LDAPDatabase
      LDAPDatabase.close
      LDAPDatabase.del
      LDAPDatabase.normalizedn
      LDAPDatabase.cachecdml
      LDAPDatabase.getDataset
      LDAPDatabase.getObjFromDataset
      LDAPDatabase.openDataset
      LDAPDatabase.setExternalDict
      LDAPDatabase.searchFilter
      LDAPDatabase.listDatasets
      
      AbstractSearchResult
      AbstractSearchResult.getitem
      AbstractSearchResult.len
      AbstractSearchResult.searchPredicate

      LDAPSearchResult
      LDAPSearchResult.getitem
      LDAPSearchResult.searchPredicate
      LDAPSearchResult.len

      AbstractResultEntry
      AbstractResultEntry.getObject
      
      LDAPResultEntry
      
