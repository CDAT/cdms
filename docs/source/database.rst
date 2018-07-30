.. _database:

database
========

.. automodule:: cdms2.database
      :members:

      AbstractDatabase
      connect
      loadString
      close
      cachecdml
      getDataset
      getObjFromDataset
      openDataset
      searchFilter
      enableCache
      disableCache
      useRequestManager
      usingRequestManager
      repr
      
      LDAPDatabase
      close
      del
      normalizedn
      cachecdml
      getDataset
      getObjFromDataset
      openDataset
      setExternalDict
      searchFilter
      listDatasets
      
      AbstractSearchResult
      getitem
      len
      searchPredicate

      LDAPSearchResult
      getitem
      searchPredicate
      len

      AbstractResultEntry
      getObject
      
      LDAPResultEntry
      
