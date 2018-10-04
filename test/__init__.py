# Copyright 2014 Google Inc. All rights reserved.
#
# Modifications Copyright (C) 2018 HeiGIT, University of Heidelberg.
#
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#

import unittest
import codecs

from cerberus import Validator, TypeDefinition
from cerberus.tests import assert_success

try:  # Python 3
    from urllib.parse import urlparse, parse_qsl
except ImportError:  # Python 2
    from urlparse import urlparse, parse_qsl

schema = {
    # 'api_key': {'type': 'string'},
    'address': {'type': 'string'},
    'attributes': {'type': ['list', 'tuple'], 'schema': {'type': 'string',
                                              'allowed': ['area', 'reachfactor', 'total_pop', 'avgspeed',
                                                          'detourfactor', 'percentage']}},
    # in directions, isochrones
    'bearings': {'type': ['list', 'tuple'], 'schema': {'type': 'list', 'schema': {'type': 'integer'}}},
    'borough': {'type': 'string'},
    'category_group_ids': {'type': 'list', 'schema': {'type': 'integer'}},
    'circle_radius': {'type': 'integer'},
    'circle_point': {'type': ['tuple', 'float']},  # not in API docu
    'continue_straight': {'type': 'string', 'allowed': ['true', 'false']},
    'coordinates': {'anyof': [{'type': ['list', 'tuple'], 'schema': {'type': 'float'}},
                              {'type': 'list', 'schema': {'type': 'list', 'schema': {'type': 'float'}}},
                              {'type': 'tuple', 'schema': {'type': 'tuple', 'schema': {'type': 'float'}}}]},
    'country': {'type': 'string'},
    'county': {'type': 'string'},
    'destinations': {
        'oneof': [{'type': 'list', 'schema': {'type': 'integer'}}, {'type': 'string', 'allowed': ['all']}]},
    'dry_run': {'type': 'string', 'allowed': ['true', 'false']},
    'elevation': {'type': 'string', 'allowed': ['true', 'false']},
    'extra_info': {'type': ['list', 'tuple'], 'schema': {'type': 'string',
                                                         'allowed': ['steepness', 'suitability', 'surface',
                                                                     'waycategory', 'waytype', 'tollways',
                                                                     'traildifficulty']}},
    'filter_category_ids': {'type': 'list', 'schema': {'type': 'integer'}},  # -> 'category_ids'?
    'filters_custom': {'type': 'dict', 'schema': {
        'name': {'type': 'list', 'schema': {
            'type': 'string'
        }},
        'wheelchair': {'type': 'list', 'schema': {
            'type': 'string', 'allowed': ['yes', 'limited', 'no', 'designated']
        }},
        'smoking': {'type': 'list', 'schema': {
            'type': 'string', 'allowed': ['dedicated', 'yes', 'separated', 'isolated', 'no', 'outside']
        }},
        'fee': {'type': 'list', 'schema': {
            'type': 'string', 'allowed': ['yes', 'no', 'str']
        }}}},
    # 'first_request_time': {'type': 'datetime'}, -> datetime.datetime -> client
    'focus_point': {'type': ['list', 'tuple'], 'schema': {'type': 'float'}},
    'format': {'type': 'string', 'allowed': ['json', 'geojson', 'gpx']},
    # 'geojson' # -> places
    'geometry': {'type': 'string', 'allowed': ['true', 'false']},  # -> directions
    # 'geometry': {'type': 'dict',
    #              'schema': {'bbox': {'type': 'list', 'schema': {'type': 'list', 'schema': {'type': 'float'}}},
    #                         'geojson': {'type': 'dict', 'schema': {'type': {'type': 'string', 'allowed': ['Point']},
    #                                                                'coordinates': {'type': 'list',
    #                                                                                'schema': {'type': 'float'}}}},
    #                         'buffer': {'type': 'integer'}}},  # -> pois
    'geometry_format': {'type': 'string', 'allowed': ['encodedpolyline', 'geojson', 'polyline']},
    'geometry_simplify': {'type': 'string', 'allowed': ['true', 'false']},
    'id': {'type': 'string'},
    'instructions': {'type': 'string', 'allowed': ['true', 'false']},
    'instructions_format': {'type': 'string', 'allowed': ['text', 'html']},
    'intersections': {'type': 'string', 'allowed': ['true', 'false']},
    'interval': {'type': 'list', 'schema': {'type': 'integer'}},
    'language': {'type': 'string',
                 'allowed': ['en', 'de', 'cn', 'es', 'ru', 'dk', 'fr', 'it', 'nl', 'br', 'se', 'tr', 'gr']},
    # different values in APIs
    'layers': {'type': 'list', 'schema': {'type': 'string'}},
    'locality': {'type': 'string'},
    'location_type': {'type': 'string', 'allowed': ['start', 'destination']},
    'locations': {'anyof': [{'type': ['list', 'tuple'], 'schema': {'type': 'float'}},
                            {'type': 'list', 'schema': {'type': 'list', 'schema': {'type': 'float'}}},
                            {'type': 'tuple', 'schema': {'type': 'tuple', 'schema': {'type': 'float'}}}]},
    'limit': {'type': 'integer'},
    'maneuvers': {'type': 'string', 'allowed': ['true', 'false']},
    'metrics': {'type': 'list', 'schema': {'type': 'string'}, 'allowed': ['distance', 'duration']},
    'neighbourhood': {'type': 'string'},
    'optimized': {'type': 'string', 'allowed': ['true', 'false']},
    'options': {'type': 'dict', 'schema': {'maximum_speed': {'type': 'integer'},
                                           'avoid_features': {'type': 'string',
                                                              'allowed': ['highways', 'tollways', 'ferries', 'tunnels',
                                                                          'pavedroads', 'unpavedroads', 'tracks',
                                                                          'fords', 'steps', 'hills']},
                                           'avoid_borders': {'type': 'string', 'allowed': ['all', 'controlled']},
                                           'avoid_countries': {'type': 'string'},
                                           'vehicle_type': {'type': 'string',
                                                            'allowed': ['hgv', 'bus', 'agricultural', 'delivery',
                                                                        'forestry', 'goods']},
                                           'profile_params': {'type': 'dict', 'schema': {
                                               'weightings': {'type': 'dict', 'schema': {
                                                   'steepness_difficulty': {'type': 'dict', 'schema': {
                                                       'level': {'type': 'integer', 'min': 0, 'max': 3}}},
                                                   'green': {'type': 'dict', 'schema': {
                                                       'factor': {'type': 'float', 'min': 0, 'max': 1}}},
                                                   'quiet': {'type': 'dict', 'schema': {
                                                       'factor': {'type': 'float', 'min': 0, 'max': 1}}}}},
                                               # 'restrictions':
                                           }},
                                           # 'avoid_polygons'
                                           }},
    # 'params': {} # -> client
    'point': {'anyof': [{'type': ['list', 'tuple'], 'schema': {'type': 'float'}},
                        {'type': 'list', 'schema': {'type': 'list', 'schema': {'type': 'float'}}},
                        {'type': 'tuple', 'schema': {'type': 'tuple', 'schema': {'type': 'float'}}}]},
    'polyline': {'type': 'string'},
    'post_json': {'type': 'dict'},
    'postalcode': {'type': 'string'},
    'profile': {'type': 'string',
                'allowed': ['driving-car', 'driving-hgv', 'foot-walking', 'foot-hiking', 'cycling-regular',
                            'cycling-road', 'cycling-safe', 'cycling-mountain', 'cycling-tour',
                            'cycling-electric']},
    'preference': {'type': 'string', 'allowed': ['fastest', 'shortest', 'recommended']},
    'radiuses': {'type': ['list', 'tuple'],
                 'schema': {'oneof': [{'type': 'float', 'allowed': [-1]}, {'type': 'float', 'min': 0}]}},
    'range_type': {'type': 'string', 'allowed': ['time', 'distance']},
    'range': {'type': 'list', 'schema': {'type': 'integer'}},
    'rect_min_x': {'type': 'float'},
    'rect_min_y': {'type': 'float'},
    'rect_max_x': {'type': 'float'},
    'rect_max_y': {'type': 'float'},
    'region': {'type': 'string'},
    'request': {'type': 'string', 'allowed': ['pois', 'list', 'stats']},
    'requests_kwargs': {'type': 'dict'},
    'resolve_locations': {'type': 'string', 'allowed': ['true', 'false']},
    'retry_counter': {'type': 'integer'},
    'roundabout_exits': {'type': 'string', 'allowed': ['true', 'false']},
    'segments': {'type': 'integer'},
    'size': {'type': 'integer'},
    'smoothing': {'type': 'float', 'min': 0, 'max': 1},
    'sortby': {'type': 'string', 'allowed': ['distance', 'category']},
    # 'sources': {'oneof': [{'type': 'list', 'schema': {'type': 'integer', 'min': 0}},
    #                       {'type': 'string', 'allowed': ['all']}]}, # -> distance_matrix
    'sources': {'type': 'list', 'schema': {'type': 'string'}, 'allowed': ['osm', 'oa', 'wof', 'gn']},  # -> geocode
    'text': {'type': 'string'},
    'units': {'type': 'string', 'allowed': ['m', 'km', 'mi']},
    'url': {'type': 'string'},
}


class TestCase(unittest.TestCase):

    def assertURLEqual(self, first, second, msg=None):
        """Check that two arguments are equivalent URLs. Ignores the order of
        query arguments.
        """
        first_parsed = urlparse(first)
        second_parsed = urlparse(second)
        self.assertEqual(first_parsed[:3], second_parsed[:3], msg)

        first_qsl = sorted(parse_qsl(first_parsed.query))
        second_qsl = sorted(parse_qsl(second_parsed.query))
        self.assertEqual(first_qsl, second_qsl, msg)

    def u(self, string):
        """Create a unicode string, compatible across all versions of Python."""
        # NOTE(cbro): Python 3-3.2 does not have the u'' syntax.
        return codecs.unicode_escape_decode(string)[0]

    def validateFormat(self, params):
        """Validates the used parameter with Cerberus."""
        # Add the tuple type
        tuple_type = TypeDefinition("tuple", (tuple), ())
        Validator.types_mapping["tuple"] = tuple_type

        assert_success(params, schema)
