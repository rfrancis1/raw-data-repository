#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Generated from FHIR 3.0.0.11832 on 2017-03-22.
#  2017, SMART Health IT.


import os
import io
import unittest
import json
from . import valueset
from .fhirdate import FHIRDate


class ValueSetTests(unittest.TestCase):
    def instantiate_from(self, filename):
        datadir = os.environ.get('FHIR_UNITTEST_DATADIR') or ''
        with io.open(os.path.join(datadir, filename), 'r', encoding='utf-8') as handle:
            js = json.load(handle)
            self.assertEqual("ValueSet", js["resourceType"])
        return valueset.ValueSet(js)
    
    def testValueSet1(self):
        inst = self.instantiate_from("valueset-example-expansion.json")
        self.assertIsNotNone(inst, "Must have instantiated a ValueSet instance")
        self.implValueSet1(inst)
        
        js = inst.as_json()
        self.assertEqual("ValueSet", js["resourceType"])
        inst2 = valueset.ValueSet(js)
        self.implValueSet1(inst2)
    
    def implValueSet1(self, inst):
        self.assertEqual(inst.compose.include[0].filter[0].op, "=")
        self.assertEqual(inst.compose.include[0].filter[0].property, "parent")
        self.assertEqual(inst.compose.include[0].filter[0].value, "LP43571-6")
        self.assertEqual(inst.compose.include[0].system, "http://loinc.org")
        self.assertEqual(inst.contact[0].telecom[0].system, "url")
        self.assertEqual(inst.contact[0].telecom[0].value, "http://hl7.org/fhir")
        self.assertEqual(inst.copyright, "This content from LOINC® is copyright © 1995 Regenstrief Institute, Inc. and the LOINC Committee, and available at no cost under the license at http://loinc.org/terms-of-use.")
        self.assertEqual(inst.date.date, FHIRDate("2015-06-22").date)
        self.assertEqual(inst.date.as_json(), "2015-06-22")
        self.assertEqual(inst.description, "This is an example value set that includes all the LOINC codes for serum/plasma cholesterol from v2.36.")
        self.assertEqual(inst.expansion.contains[0].code, "14647-2")
        self.assertEqual(inst.expansion.contains[0].display, "Cholesterol [Moles/volume] in Serum or Plasma")
        self.assertEqual(inst.expansion.contains[0].system, "http://loinc.org")
        self.assertEqual(inst.expansion.contains[0].version, "2.50")
        self.assertTrue(inst.expansion.contains[1].abstract)
        self.assertEqual(inst.expansion.contains[1].contains[0].code, "2093-3")
        self.assertEqual(inst.expansion.contains[1].contains[0].display, "Cholesterol [Mass/volume] in Serum or Plasma")
        self.assertEqual(inst.expansion.contains[1].contains[0].system, "http://loinc.org")
        self.assertEqual(inst.expansion.contains[1].contains[0].version, "2.50")
        self.assertEqual(inst.expansion.contains[1].contains[1].code, "48620-9")
        self.assertEqual(inst.expansion.contains[1].contains[1].display, "Cholesterol [Mass/volume] in Serum or Plasma ultracentrifugate")
        self.assertEqual(inst.expansion.contains[1].contains[1].system, "http://loinc.org")
        self.assertEqual(inst.expansion.contains[1].contains[1].version, "2.50")
        self.assertEqual(inst.expansion.contains[1].contains[2].code, "9342-7")
        self.assertEqual(inst.expansion.contains[1].contains[2].display, "Cholesterol [Percentile]")
        self.assertEqual(inst.expansion.contains[1].contains[2].system, "http://loinc.org")
        self.assertEqual(inst.expansion.contains[1].contains[2].version, "2.50")
        self.assertEqual(inst.expansion.contains[1].display, "Cholesterol codes")
        self.assertTrue(inst.expansion.contains[2].abstract)
        self.assertEqual(inst.expansion.contains[2].contains[0].code, "2096-6")
        self.assertEqual(inst.expansion.contains[2].contains[0].display, "Cholesterol/Triglyceride [Mass Ratio] in Serum or Plasma")
        self.assertEqual(inst.expansion.contains[2].contains[0].system, "http://loinc.org")
        self.assertEqual(inst.expansion.contains[2].contains[0].version, "2.50")
        self.assertEqual(inst.expansion.contains[2].contains[1].code, "35200-5")
        self.assertEqual(inst.expansion.contains[2].contains[1].display, "Cholesterol/Triglyceride [Mass Ratio] in Serum or Plasma")
        self.assertEqual(inst.expansion.contains[2].contains[1].system, "http://loinc.org")
        self.assertEqual(inst.expansion.contains[2].contains[1].version, "2.50")
        self.assertEqual(inst.expansion.contains[2].contains[2].code, "48089-7")
        self.assertEqual(inst.expansion.contains[2].contains[2].display, "Cholesterol/Apolipoprotein B [Molar ratio] in Serum or Plasma")
        self.assertEqual(inst.expansion.contains[2].contains[2].system, "http://loinc.org")
        self.assertEqual(inst.expansion.contains[2].contains[2].version, "2.50")
        self.assertEqual(inst.expansion.contains[2].contains[3].code, "55838-7")
        self.assertEqual(inst.expansion.contains[2].contains[3].display, "Cholesterol/Phospholipid [Molar ratio] in Serum or Plasma")
        self.assertEqual(inst.expansion.contains[2].contains[3].system, "http://loinc.org")
        self.assertEqual(inst.expansion.contains[2].contains[3].version, "2.50")
        self.assertEqual(inst.expansion.contains[2].display, "Cholesterol Ratios")
        self.assertEqual(inst.expansion.extension[0].url, "http://hl7.org/fhir/StructureDefinition/valueset-expansionSource")
        self.assertEqual(inst.expansion.extension[0].valueUri, "http://hl7.org/fhir/ValueSet/example-extensional")
        self.assertEqual(inst.expansion.identifier, "urn:uuid:42316ff8-2714-4680-9980-f37a6d1a71bc")
        self.assertEqual(inst.expansion.offset, 0)
        self.assertEqual(inst.expansion.parameter[0].name, "version")
        self.assertEqual(inst.expansion.parameter[0].valueString, "2.50")
        self.assertEqual(inst.expansion.timestamp.date, FHIRDate("2015-06-22T13:56:07Z").date)
        self.assertEqual(inst.expansion.timestamp.as_json(), "2015-06-22T13:56:07Z")
        self.assertEqual(inst.expansion.total, 8)
        self.assertTrue(inst.experimental)
        self.assertEqual(inst.id, "example-expansion")
        self.assertEqual(inst.meta.profile[0], "http://hl7.org/fhir/StructureDefinition/shareablevalueset")
        self.assertEqual(inst.name, "LOINC Codes for Cholesterol in Serum/Plasma")
        self.assertEqual(inst.publisher, "FHIR Project team")
        self.assertEqual(inst.status, "draft")
        self.assertEqual(inst.text.status, "generated")
        self.assertEqual(inst.url, "http://hl7.org/fhir/ValueSet/example-expansion")
        self.assertEqual(inst.version, "20150622")
    
    def testValueSet2(self):
        inst = self.instantiate_from("valueset-example-inactive.json")
        self.assertIsNotNone(inst, "Must have instantiated a ValueSet instance")
        self.implValueSet2(inst)
        
        js = inst.as_json()
        self.assertEqual("ValueSet", js["resourceType"])
        inst2 = valueset.ValueSet(js)
        self.implValueSet2(inst2)
    
    def implValueSet2(self, inst):
        self.assertTrue(inst.compose.inactive)
        self.assertEqual(inst.compose.include[0].filter[0].op, "descendent-of")
        self.assertEqual(inst.compose.include[0].filter[0].property, "concept")
        self.assertEqual(inst.compose.include[0].filter[0].value, "_ActMoodPredicate")
        self.assertEqual(inst.compose.include[0].system, "http://hl7.org/fhir/v3/ActMood")
        self.assertEqual(inst.description, "HL7 v3 ActMood Prdicate codes, including inactive codes")
        self.assertEqual(inst.expansion.contains[0].code, "CRT")
        self.assertEqual(inst.expansion.contains[0].display, "criterion")
        self.assertTrue(inst.expansion.contains[0].inactive)
        self.assertEqual(inst.expansion.contains[0].system, "http://hl7.org/fhir/v3/ActMood")
        self.assertEqual(inst.expansion.contains[1].code, "EXPEC")
        self.assertEqual(inst.expansion.contains[1].contains[0].code, "GOL")
        self.assertEqual(inst.expansion.contains[1].contains[0].display, "goal")
        self.assertEqual(inst.expansion.contains[1].contains[0].system, "http://hl7.org/fhir/v3/ActMood")
        self.assertEqual(inst.expansion.contains[1].contains[1].code, "RSK")
        self.assertEqual(inst.expansion.contains[1].contains[1].display, "risk")
        self.assertEqual(inst.expansion.contains[1].contains[1].system, "http://hl7.org/fhir/v3/ActMood")
        self.assertEqual(inst.expansion.contains[1].display, "expectation")
        self.assertEqual(inst.expansion.contains[1].system, "http://hl7.org/fhir/v3/ActMood")
        self.assertEqual(inst.expansion.contains[2].code, "OPT")
        self.assertEqual(inst.expansion.contains[2].display, "option")
        self.assertEqual(inst.expansion.contains[2].system, "http://hl7.org/fhir/v3/ActMood")
        self.assertEqual(inst.expansion.identifier, "urn:uuid:46c00b3f-003a-4f31-9d4b-ea2de58b2a99")
        self.assertEqual(inst.expansion.timestamp.date, FHIRDate("2017-02-26T10:00:00Z").date)
        self.assertEqual(inst.expansion.timestamp.as_json(), "2017-02-26T10:00:00Z")
        self.assertEqual(inst.id, "inactive")
        self.assertEqual(inst.name, "Example-inactive")
        self.assertEqual(inst.status, "draft")
        self.assertEqual(inst.text.status, "generated")
        self.assertEqual(inst.title, "Example with inactive codes")
        self.assertEqual(inst.url, "http://hl7.org/fhir/ValueSet/inactive")
    
    def testValueSet3(self):
        inst = self.instantiate_from("valueset-example-intensional.json")
        self.assertIsNotNone(inst, "Must have instantiated a ValueSet instance")
        self.implValueSet3(inst)
        
        js = inst.as_json()
        self.assertEqual("ValueSet", js["resourceType"])
        inst2 = valueset.ValueSet(js)
        self.implValueSet3(inst2)
    
    def implValueSet3(self, inst):
        self.assertEqual(inst.compose.exclude[0].concept[0].code, "5932-9")
        self.assertEqual(inst.compose.exclude[0].concept[0].display, "Cholesterol [Presence] in Blood by Test strip")
        self.assertEqual(inst.compose.exclude[0].system, "http://loinc.org")
        self.assertEqual(inst.compose.include[0].filter[0].op, "=")
        self.assertEqual(inst.compose.include[0].filter[0].property, "parent")
        self.assertEqual(inst.compose.include[0].filter[0].value, "LP43571-6")
        self.assertEqual(inst.compose.include[0].system, "http://loinc.org")
        self.assertEqual(inst.contact[0].name, "FHIR project team")
        self.assertEqual(inst.contact[0].telecom[0].system, "url")
        self.assertEqual(inst.contact[0].telecom[0].value, "http://hl7.org/fhir")
        self.assertEqual(inst.copyright, "This content from LOINCÂ® is copyright Â© 1995 Regenstrief Institute, Inc. and the LOINC Committee, and available at no cost under the license at http://loinc.org/terms-of-use")
        self.assertEqual(inst.date.date, FHIRDate("2015-06-22").date)
        self.assertEqual(inst.date.as_json(), "2015-06-22")
        self.assertEqual(inst.description, "This is an example value set that includes all the LOINC codes for serum/plasma cholesterol from v2.36.")
        self.assertTrue(inst.experimental)
        self.assertEqual(inst.id, "example-intensional")
        self.assertEqual(inst.identifier[0].system, "http://acme.com/identifiers/valuesets")
        self.assertEqual(inst.identifier[0].value, "loinc-cholesterol-ext")
        self.assertEqual(inst.meta.profile[0], "http://hl7.org/fhir/StructureDefinition/shareablevalueset")
        self.assertEqual(inst.name, "LOINC Codes for Cholesterol in Serum/Plasma")
        self.assertEqual(inst.publisher, "HL7 International")
        self.assertEqual(inst.status, "draft")
        self.assertEqual(inst.text.status, "generated")
        self.assertEqual(inst.url, "http://hl7.org/fhir/ValueSet/example-intensional")
        self.assertEqual(inst.version, "20150622")
    
    def testValueSet4(self):
        inst = self.instantiate_from("valueset-example-yesnodontknow.json")
        self.assertIsNotNone(inst, "Must have instantiated a ValueSet instance")
        self.implValueSet4(inst)
        
        js = inst.as_json()
        self.assertEqual("ValueSet", js["resourceType"])
        inst2 = valueset.ValueSet(js)
        self.implValueSet4(inst2)
    
    def implValueSet4(self, inst):
        self.assertEqual(inst.compose.include[0].valueSet[0], "http://hl7.org/fhir/ValueSet/v2-0136")
        self.assertEqual(inst.compose.include[1].concept[0].code, "asked")
        self.assertEqual(inst.compose.include[1].concept[0].display, "Don't know")
        self.assertEqual(inst.compose.include[1].system, "http://hl7.org/fhir/data-absent-reason")
        self.assertEqual(inst.description, "For Capturing simple yes-no-don't know answers")
        self.assertEqual(inst.expansion.contains[0].code, "Y")
        self.assertEqual(inst.expansion.contains[0].display, "Yes")
        self.assertEqual(inst.expansion.contains[0].system, "http://hl7.org/fhir/v2/0136")
        self.assertEqual(inst.expansion.contains[1].code, "N")
        self.assertEqual(inst.expansion.contains[1].display, "No")
        self.assertEqual(inst.expansion.contains[1].system, "http://hl7.org/fhir/v2/0136")
        self.assertEqual(inst.expansion.contains[2].code, "asked")
        self.assertEqual(inst.expansion.contains[2].display, "Don't know")
        self.assertEqual(inst.expansion.contains[2].system, "http://hl7.org/fhir/data-absent-reason")
        self.assertEqual(inst.expansion.identifier, "urn:uuid:bf99fe50-2c2b-41ad-bd63-bee6919810b4")
        self.assertEqual(inst.expansion.timestamp.date, FHIRDate("2015-07-14T10:00:00Z").date)
        self.assertEqual(inst.expansion.timestamp.as_json(), "2015-07-14T10:00:00Z")
        self.assertEqual(inst.id, "yesnodontknow")
        self.assertEqual(inst.name, "Yes/No/Don't Know")
        self.assertEqual(inst.status, "draft")
        self.assertEqual(inst.text.status, "generated")
        self.assertEqual(inst.url, "http://hl7.org/fhir/ValueSet/yesnodontknow")
    
    def testValueSet5(self):
        inst = self.instantiate_from("valueset-example.json")
        self.assertIsNotNone(inst, "Must have instantiated a ValueSet instance")
        self.implValueSet5(inst)
        
        js = inst.as_json()
        self.assertEqual("ValueSet", js["resourceType"])
        inst2 = valueset.ValueSet(js)
        self.implValueSet5(inst2)
    
    def implValueSet5(self, inst):
        self.assertTrue(inst.compose.inactive)
        self.assertEqual(inst.compose.include[0].concept[0].code, "14647-2")
        self.assertEqual(inst.compose.include[0].concept[0].display, "Cholesterol [Moles/Volume]")
        self.assertEqual(inst.compose.include[0].concept[1].code, "2093-3")
        self.assertEqual(inst.compose.include[0].concept[1].display, "Cholesterol [Mass/Volume]")
        self.assertEqual(inst.compose.include[0].concept[2].code, "35200-5")
        self.assertEqual(inst.compose.include[0].concept[2].display, "Cholesterol [Mass Or Moles/Volume]")
        self.assertEqual(inst.compose.include[0].concept[3].code, "9342-7")
        self.assertEqual(inst.compose.include[0].concept[3].display, "Cholesterol [Percentile]")
        self.assertEqual(inst.compose.include[0].system, "http://loinc.org")
        self.assertEqual(inst.compose.include[0].version, "2.36")
        self.assertEqual(inst.compose.lockedDate.date, FHIRDate("2012-06-13").date)
        self.assertEqual(inst.compose.lockedDate.as_json(), "2012-06-13")
        self.assertEqual(inst.contact[0].name, "FHIR project team")
        self.assertEqual(inst.contact[0].telecom[0].system, "url")
        self.assertEqual(inst.contact[0].telecom[0].value, "http://hl7.org/fhir")
        self.assertEqual(inst.copyright, "This content from LOINC ® is copyright © 1995 Regenstrief Institute, Inc. and the LOINC Committee, and available at no cost under the license at http://loinc.org/terms-of-use.")
        self.assertEqual(inst.date.date, FHIRDate("2015-06-22").date)
        self.assertEqual(inst.date.as_json(), "2015-06-22")
        self.assertEqual(inst.description, "This is an example value set that includes all the LOINC codes for serum/plasma cholesterol from v2.36.")
        self.assertTrue(inst.experimental)
        self.assertEqual(inst.id, "example-extensional")
        self.assertEqual(inst.identifier[0].system, "http://acme.com/identifiers/valuesets")
        self.assertEqual(inst.identifier[0].value, "loinc-cholesterol-int")
        self.assertEqual(inst.meta.profile[0], "http://hl7.org/fhir/StructureDefinition/shareablevalueset")
        self.assertEqual(inst.name, "LOINC Codes for Cholesterol in Serum/Plasma")
        self.assertEqual(inst.publisher, "HL7 International")
        self.assertEqual(inst.status, "draft")
        self.assertEqual(inst.text.status, "generated")
        self.assertEqual(inst.url, "http://hl7.org/fhir/ValueSet/example-extensional")
        self.assertEqual(inst.version, "20150622")
    
    def testValueSet6(self):
        inst = self.instantiate_from("valueset-list-example-codes.json")
        self.assertIsNotNone(inst, "Must have instantiated a ValueSet instance")
        self.implValueSet6(inst)
        
        js = inst.as_json()
        self.assertEqual("ValueSet", js["resourceType"])
        inst2 = valueset.ValueSet(js)
        self.implValueSet6(inst2)
    
    def implValueSet6(self, inst):
        self.assertEqual(inst.compose.include[0].system, "http://hl7.org/fhir/list-example-use-codes")
        self.assertEqual(inst.contact[0].telecom[0].system, "url")
        self.assertEqual(inst.contact[0].telecom[0].value, "http://hl7.org/fhir")
        self.assertEqual(inst.date.date, FHIRDate("2017-03-21T21:41:32+00:00").date)
        self.assertEqual(inst.date.as_json(), "2017-03-21T21:41:32+00:00")
        self.assertEqual(inst.description, "Example use codes for the List resource - typical kinds of use.")
        self.assertTrue(inst.experimental)
        self.assertEqual(inst.extension[0].url, "http://hl7.org/fhir/StructureDefinition/structuredefinition-ballot-status")
        self.assertEqual(inst.extension[0].valueString, "Informative")
        self.assertEqual(inst.extension[1].url, "http://hl7.org/fhir/StructureDefinition/structuredefinition-fmm")
        self.assertEqual(inst.extension[1].valueInteger, 1)
        self.assertEqual(inst.extension[2].url, "http://hl7.org/fhir/StructureDefinition/structuredefinition-wg")
        self.assertEqual(inst.extension[2].valueCode, "fhir")
        self.assertEqual(inst.id, "list-example-codes")
        self.assertEqual(inst.identifier[0].system, "urn:ietf:rfc:3986")
        self.assertEqual(inst.identifier[0].value, "urn:oid:2.16.840.1.113883.4.642.3.307")
        self.assertTrue(inst.immutable)
        self.assertEqual(inst.meta.lastUpdated.date, FHIRDate("2017-03-21T21:41:32.180+00:00").date)
        self.assertEqual(inst.meta.lastUpdated.as_json(), "2017-03-21T21:41:32.180+00:00")
        self.assertEqual(inst.meta.profile[0], "http://hl7.org/fhir/StructureDefinition/shareablevalueset")
        self.assertEqual(inst.name, "Example Use Codes for List")
        self.assertEqual(inst.publisher, "FHIR Project")
        self.assertEqual(inst.status, "draft")
        self.assertEqual(inst.text.status, "generated")
        self.assertEqual(inst.url, "http://hl7.org/fhir/ValueSet/list-example-codes")
        self.assertEqual(inst.version, "3.0.0")
