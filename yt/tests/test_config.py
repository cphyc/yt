"""
Tests for yt.config
"""
#-----------------------------------------------------------------------------
# Copyright (c) 2018, yt Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------
from nose.tools import assert_equal
from unittest import TestCase

from yt.config import YTConfig, ytcfg_defaults
import os

class ConfigTest(TestCase):
    @classmethod
    def setupClass(cls):
        # Create new configuration
        cls.cfg = YTConfig({'yt': ytcfg_defaults})
        cls.cfg.update({'yt': {'dummy': ''}})

        cls.cfg.update({'config':
                        {'foo': {'bar1': {'cmap': 'viridis'},
                                 'bar2': {'log': False}}}})

    def test_variable_expansion(self):
        '''Test variables are correctly expanded'''
        cfg = self.cfg
        # Check that the path are correctly expanded
        test_paths = ('~/test/path', '$HOME/test/path')
        for test_path in test_paths:
            cfg['yt', 'dummy'] = test_path

            expected = os.path.expanduser(os.path.expandvars(test_path))
            answer = cfg.get(('yt', 'dummy'))

            assert_equal(expected, answer)

    def test_getter(self):
        '''Test objects getter/setter using dict-like syntax'''
        cfg = self.cfg
        for key in ytcfg_defaults.keys():
            assert_equal(cfg['yt', key], cfg.get(('yt', key)))

        cfg['yt', 'dummy'] = 'bar'
        assert_equal(cfg['yt', 'dummy'], 'bar')

    def test_get_field_config(self):
        '''Test iterator over config'''
        cfg = self.cfg

        def dummy_serializer(*args):
            return args

        # Test with one variable
        keys = ('cmap', )
        getter = {'cmap': 'get'}

        expected = [(('foo', 'bar1'), 'cmap', 'viridis')]
        result = list(cfg.get_field_config(keys, dummy_serializer, getter))
        
        assert_equal(expected, result)

        # Test with one variable
        keys = ('log', )
        getter = {'log': 'getboolean'}

        expected = [(('foo', 'bar2'), 'log', False)]
        result = list(cfg.get_field_config(keys, dummy_serializer, getter))
        
        assert_equal(expected, result)

        # Test with two variables
        keys = ('cmap', 'log')
        getter = {'cmap': 'get', 'log': 'getboolean'}

        expected = [(('foo', 'bar1'), 'cmap', 'viridis'),
                    (('foo', 'bar2'), 'log', False)]
        result = list(cfg.get_field_config(keys, dummy_serializer, getter))
        
        assert_equal(expected, result)
        
