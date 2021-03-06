# -*- coding: utf-8 -*-

import unittest
from feature_selection.feature_selection import FeatureSelection

class TestFeatureSelection(unittest.TestCase):

    def test_empty_feature_selection(self):
        y = '''
        '''
        f = FeatureSelection(y)
        self.assertFalse(f.valid)

    def test_key_union_and_filters(self):
        y = '''
        waterways:
            types: 
                - lines
                - polygons
            select:
                - name
                - waterway
        buildings:
            types:
                - points
                - lines
                - polygons
            select:
                - name
                - building
            where: building IS NOT NULL
        '''
        f = FeatureSelection(y)
        self.assertEquals(f.themes,['buildings','waterways'])
        self.assertEquals(f.geom_types('waterways'),['lines','polygons'])
        self.assertEquals(f.key_selections('waterways'),['name','waterway'])
        self.assertEquals(f.filter_clause('waterways'),'1') # SELECT WHERE 1
        self.assertEquals(f.key_union(), ['building','name','waterway'])
        self.assertEquals(f.key_union('points'), ['building','name'])
        self.assertEquals(f.filter_clause('buildings'),'building IS NOT NULL')

    def test_sqls(self):
        y = '''
        buildings:
            types:
                - points
                - polygons
            select:
                - name
                - addr:housenumber
        '''
        f = FeatureSelection(y)
        create_sqls, index_sqls = f.sqls
        self.assertEquals(create_sqls[0],'CREATE TABLE buildings_points AS SELECT geom,osm_id,"name","addr:housenumber" FROM planet_osm_point WHERE (1)')
        self.assertEquals(create_sqls[1],'CREATE TABLE buildings_polygons AS SELECT geom,osm_id,osm_way_id,"name","addr:housenumber" FROM planet_osm_polygon WHERE (1)')

    def test_zindex(self):
        y = '''
        roads:
            types:
                - lines 
            select:
                - highway
        '''
        f = FeatureSelection(y)
        create_sqls, index_sqls = f.sqls
        self.assertEquals(create_sqls[0],'CREATE TABLE roads_lines AS SELECT geom,osm_id,"highway","z_index" FROM planet_osm_line WHERE (1)')


    def test_unsafe_yaml(self):
        y = '''
        !!python/object:feature_selection.feature_selection.FeatureSelection
        a: 0
        '''
        f = FeatureSelection(y)
        self.assertFalse(f.valid)
        self.assertEqual(1,len(f.errors))

    def test_malformed_yaml(self):
        # if it's not a valid YAML document
        # TODO: errors for if yaml indentation is incorrect
        y = '''
        all
            select:
                - name
        '''
        f = FeatureSelection(y)
        self.assertFalse(f.valid)

    def test_minimal_yaml(self):
        # the shortest valid feature selection
        y = '''
        all: 
            select:
                - name
        '''
        f = FeatureSelection(y)
        self.assertTrue(f.valid)
        self.assertEqual(f.geom_types('all'),['points','lines','polygons'])

    def test_unspecified_yaml(self):
        # top level is a list and not a dict
        y = '''
        - all: 
            select:
                - name
        '''
        f = FeatureSelection(y)
        self.assertFalse(f.valid)
        self.assertEqual(f.errors[0],"YAML must be dict, not list")

    def test_dash_spacing_yaml(self):
        # top level is a list and not a dict
        y = '''
        all: 
          select:
            -name
        '''
        f = FeatureSelection(y)
        self.assertFalse(f.valid)

    def test_no_select_yaml(self):
        # top level is a list and not a dict
        y = '''
        all: 
          -select:
            - name
        '''
        f = FeatureSelection(y)
        self.assertFalse(f.valid)
        self.assertEqual(f.errors[0],"Each theme must have a 'select' key")

    # refer to https://taginfo.openstreetmap.org/keys
    def test_valid_invalid_key_yaml(self):
        y = '''
        all: 
          select:
            - has space
            - has_underscore
            - has:colon
            - UPPERCASE
        '''
        f = FeatureSelection(y)
        self.assertTrue(f.valid)
        y = '''
        all: 
          select:
            - na?me
        '''
        f = FeatureSelection(y)
        self.assertFalse(f.valid)
        self.assertEqual(f.errors[0],"Invalid OSM key: na?me")
        y = '''
        all: 
          select:
            -
        '''
        f = FeatureSelection(y)
        self.assertFalse(f.valid)
        self.assertEqual(f.errors[0],"Missing OSM key")

    def test_passes_sqlvalidator_errors(self):
        y = '''
        buildings:
            select:
                - name
                - addr:housenumber
            where: addr:housenumber IS NOT NULL
        '''
        f = FeatureSelection(y)
        self.assertFalse(f.valid)
        self.assertEquals(f.errors[0], "SQL WHERE Invalid: identifier with colon : must be in double quotes.")

    def test_enforces_subset_columns(self):
        y = '''
        buildings:
            types:
                - polygons
            select:
                - column1 
            where: column2 IS NOT NULL
        other:
            types:
                - points
            select:
                - column3
        '''
        f = FeatureSelection(y)
        self.assertTrue(f.valid)
        self.assertEquals(f.key_union(), ['column1','column2','column3'])
        self.assertEquals(f.key_union('points'), ['column3'])

