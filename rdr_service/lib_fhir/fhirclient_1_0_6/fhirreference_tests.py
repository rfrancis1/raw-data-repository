# -*- coding: utf-8 -*-

import io
import json
import logging
import os.path
import unittest

from . import models.bundle as bundle
from . import models.medication as medication
from . import models.patient as patient
from . import models.questionnaire as questionnaire
from . import models.resource as resource
from . import models.valueset as valueset
from . import server

logging.basicConfig(level=logging.CRITICAL)


class TestResourceReference(unittest.TestCase):
    
    def testContainedResourceDetection(self):
        with io.open('test_contained_resource.json', 'r', encoding='utf-8') as h:
            data = json.load(h)
        q = questionnaire.Questionnaire(data)
        self.assertIsNotNone(q, "Must instantiate Questionnaire")
        self.assertEqual('Questionnaire', q.resource_name)
        
        group = q.group.group[3]
        self.assertEqual('Observation.subject', group.linkId)
        question = group.question[0]
        self.assertEqual('Observation.subject._type', question.linkId)
        self.assertIsNotNone(question.options)
        with self.assertRaises(Exception):
            question.options.resolved()
        
        # 1st resolve, extracting from contained resources
        contained = question.options.resolved(medication.Medication)
        self.assertIsNone(contained, "Must not resolve on resource type mismatch")
        contained = question.options.resolved(valueset.ValueSet)
        self.assertIsNotNone(contained, "Must resolve contained ValueSet")
        self.assertEqual('ValueSet', contained.resource_name)
        self.assertEqual('Type options for Observation.subject', contained.name)
        
        # 2nd resolve, should pull from cache
        contained = question.options.resolved(medication.Medication)
        self.assertIsNone(contained, "Must not resolve on resource type mismatch")
        contained = question.options.resolved(resource.Resource)
        self.assertIsNotNone(contained, "Must resolve contained ValueSet even if requesting `Resource`")
        contained = question.options.resolved(valueset.ValueSet)
        self.assertIsNotNone(contained, "Must resolve contained ValueSet")
        self.assertEqual('ValueSet', contained.resource_name)
    
    def testRelativeReference(self):
        with io.open('test_relative_reference.json', 'r', encoding='utf-8') as h:
            data = json.load(h)
        q = questionnaire.Questionnaire(data)
        self.assertIsNotNone(q, "Must instantiate Questionnaire")
        self.assertEqual('Questionnaire', q.resource_name)
        q._server = MockServer()
        
        group = q.group.group[0]
        self.assertEqual('Observation.subject', group.linkId)
        question = group.question[0]
        self.assertEqual('Observation.subject._type', question.linkId)
        self.assertIsNotNone(question.options)
        with self.assertRaises(Exception):
            question.options.resolved()
        
        # resolve relative resource
        relative = question.options.resolved(valueset.ValueSet)
        self.assertIsNotNone(relative, "Must resolve relative ValueSet")
        self.assertEqual('ValueSet', relative.resource_name)
        self.assertEqual('Type options for Observation.subject', relative.name)
        
        # 2nd resolve, should pull from cache
        relative = question.options.resolved(medication.Medication)
        self.assertIsNone(relative, "Must not resolve on resource type mismatch")
        relative = question.options.resolved(resource.Resource)
        self.assertIsNotNone(relative, "Must resolve relative ValueSet even if requesting `Resource`")
    
    def testBundleReferences(self):
        with io.open('test_bundle.json', 'r', encoding='utf-8') as h:
            data = json.load(h)
        b = bundle.Bundle(data)
        self.assertIsNotNone(b, "Must instantiate Bundle")
        self.assertEqual('Bundle', b.resource_name)
        #b._server = MockServer()
        
        # get resources
        pat23 = b.entry[0].resource
        self.assertEqual('Patient', pat23.resource_name)
        self.assertEqual('Darth', pat23.name[0].given[0])
        patURN = b.entry[1].resource
        self.assertEqual('Patient', patURN.resource_name)
        self.assertEqual('Ben', patURN.name[0].given[0])
        obs123 = b.entry[2].resource
        self.assertEqual('Observation', obs123.resource_name)
        obs56 = b.entry[3].resource
        self.assertEqual('Observation', obs56.resource_name)
        obs34 = b.entry[4].resource
        self.assertEqual('Observation', obs34.resource_name)
        
        # test resolving w/o server (won't work)
        res = obs123.subject.resolved(patient.Patient)
        self.assertIsNone(res)
        
        # test resolving with server
        b._server = MockServer()
        res = obs123.subject.resolved(patient.Patient)
        self.assertEqual(res, pat23)
        res = obs123.subject.resolved(medication.Medication)
        self.assertIsNone(res, "Must not resolve on type mismatch")
        res = obs56.subject.resolved(patient.Patient)
        self.assertEqual(res, patURN)
        res = obs34.subject.resolved(patient.Patient)
        self.assertIsNone(res, "Must not resolve Patient on same server but different endpoint")


class MockServer(server.FHIRServer):
    """ Reads local files.
    """
    
    def __init__(self):
        super().__init__(None, base_uri='https://fhir.smarthealthit.org')
    
    def request_json(self, path, nosign=False):
        assert path
        parts = os.path.split(path)
        filename = '_'.join(parts) + '.json'
        with io.open(filename, 'r', encoding='utf-8') as handle:
            return json.load(handle)
        return None

