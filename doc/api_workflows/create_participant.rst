************************************************************
Create Participant Workflow
************************************************************

Creating a Participant
============================================================
To create a Participant, send a POST request to the ``/Participant`` resource with an empty JSON object or an ``externalId`` in the request body.  The response is a Participant object with newly-created ids.
The optional ``externalId`` should be an internal (to the calling client) ID used to confirm the participant does not already exist.
If the ``externalId`` does already exist in the RDR system, the existing participant is returned.

Examples
------------------------------------------------------------
.. topic:: Create Participant

    **Request:**

    ::

      POST /rdr/v1/Participant
      Body: {} or {externalId: <internal id>}

    **Response**:

    ::

      {
          "participantId": "P513996261",
          "externalId": null,
          "hpoId": "UNSET",
          "awardee": "UNSET",
          "organization": "UNSET",
          "biobankId": "Z217149493",
          "lastModified": "2019-09-23T13:58:41",
          "signUpTime": "2019-09-23T13:58:41",
          "providerLink": null,
          "withdrawalStatus": "NOT_WITHDRAWN",
          "withdrawalReason": "UNSET",
          "withdrawalReasonJustification": null,
          "withdrawalAuthored": null,
          "suspensionStatus": "NOT_SUSPENDED",
          "site": "UNSET",
          "meta": {
              "versionId": "W/\"1\""
          }
      }


The ``/Participant`` Resource
============================================================

The Participant is a very thin resource—essentially it has a set of identifiers including:

* ``participantId``: PMI-specific ID generated by the RDR and used for tracking/linking participant data. Human-readable 10-character string beginning with ``P``.
* ``biobankId``: PMI-specific ID generated by the RDR and used exclusively for communicating with the biobank. Human-readable 10-character string beginning with ``B``.

* ``providerLink``: list of "provider link" objects indicating that this participant is known to a provider, including:
  * ``primary``: ``true`` | ``false``, indicating whether this provider is the "main" provider responsible for recruiting a participant and performing physical measurements and biospecimen collection.
  * ``organization``: Reference to an organizational pairing level below awardee, like ``organization: WISCONSIN_MADISON``

* ``awardee``: Reference to an awardee  pairing level, like ``awardee: AZ_TUCSON``

* ``site``: Reference to a physical location pairing level below organization. Site name are a subset of google group, like ``site: hpo-site-uabkirklin``
* ``identifier``: array of FHIR `identifiers <https://www.hl7.org/fhir/datatypes.html#Identifier>`_  with ``system`` and ``value`` indicating medical record numbers by which this participant is known.
* ``withdrawalStatus``: ``NOT_WITHDRAWN`` | ``NO_USE``; indicates whether the participant
  has withdrawn from the study, and does not want their data used in future
* ``suspensionStatus``: ``NOT_SUSPENDED`` | ``NO_CONTACT``; indicates whether the participant has indicated they do not want to be contacted anymore.
