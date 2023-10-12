import unittest

import numpy as np

from iblatlas.regions import BrainRegions
from iblbrainviewer.api import DEFAULT_VOLUME_SHAPE, FeatureUploader


@unittest.SkipTest
class TestApp(unittest.TestCase):

    def setUp(self):
        # Bucket authentication token for tests.
        self.token = 'bb77d7eb-509b-4ed2-9df6-9907c3cd6ab9'

    def test_client(self):
        bucket_uuid = f'my_bucket_{self.token}'
        fname = 'newfeatures'

        acronyms = ['CP', 'SUB']
        values = [42, 420]
        tree = {'dir': {'my custom features': fname}}

        # Create or load the bucket.
        up = FeatureUploader(bucket_uuid, tree=tree, token=self.token)

        # Create the features.
        if not up.features_exist(fname):
            up.create_features(fname, acronyms, values, hemisphere='left')

        # Patch the bucket metadata.
        tree['duplicate features'] = fname
        up.patch_bucket(tree=tree)

        # List all features in the bucket.
        print(up.list_features())

        # Retrieve one feature.
        features = up.get_features(fname)
        print(features)

        # Patch the features.
        values[1] = 10
        up.patch_features(fname, acronyms, values, hemisphere='left')

        # Delete the bucket
        # up.delete_bucket()

    def test_client_2(self):

        br = BrainRegions()

        n = 300
        mapping = 'beryl'
        fname1 = 'fet1'
        fname2 = 'fet2'
        bucket = 'test_bucket'
        tree = {'dir': {'custom features 1': fname1}, 'custom features 2': fname2}

        # Beryl regions.
        acronyms = np.unique(br.acronym[br.mappings[mapping.title()]])[:n]
        n = len(acronyms)
        values1 = np.random.randn(n)
        values2 = np.random.randn(n)
        assert len(acronyms) == len(values1)
        assert len(acronyms) == len(values2)

        # Create or load the bucket.
        up = FeatureUploader(bucket, tree=tree, token=self.token)

        # Create the features.
        if not up.features_exist(fname1):
            up.create_features(fname1, acronyms, values1, hemisphere='left')
        if not up.features_exist(fname2):
            up.create_features(fname2, acronyms, values2, hemisphere='left')

        url = up.get_buckets_url([bucket])
        print(url)

    def test_client_volume(self):

        fname = 'myvolume'
        bucket = 'test_bucket'
        tree = {'my test volume': fname}

        # Create or load the bucket.
        up = FeatureUploader(bucket, tree=tree, token=self.token)

        # Create a ball volume.
        shape = DEFAULT_VOLUME_SHAPE
        arr = np.zeros(shape, dtype=np.float32)
        center = (shape[0] // 2, shape[1] // 2, shape[2] // 2)
        radius = 100
        i, j, k = np.ogrid[:shape[0], :shape[1], :shape[2]]
        distance = np.sqrt((i - center[0])**2 + (j - center[1])**2 + (k - center[2])**2)
        arr[distance <= radius] = 1.0

        # Create the features.
        desc = "this is my volume"
        if not up.features_exist(fname):
            up.create_volume(fname, arr, desc=desc)

        # Retrieve one feature.
        features = up.get_features(fname)
        self.assertTrue(features['feature_data']['volume'])
        self.assertEqual(features['short_desc'], desc)

        # Patch the features.
        arr[distance <= radius] = 2.0
        up.patch_volume(fname, arr)
