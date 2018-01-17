import os
import glob
import re

from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly
import numpy as np


class PCRasterMap:
    def __init__(self, pcr_map_filename):
        dataset = gdal.Open(pcr_map_filename.encode('utf-8'), GA_ReadOnly)
        self.filename = pcr_map_filename
        self.dataset = dataset
        self.geo_transform = dataset.GetGeoTransform()
        self.cols = self.dataset.RasterXSize
        self.rows = self.dataset.RasterYSize
        self.band = self.dataset.GetRasterBand(1)

    def close(self):
        self.band = None
        self.dataset = None

    @property
    def data(self):
        data = self.band.ReadAsArray(0, 0, self.cols, self.rows)
        return data

    @property
    def mv(self):
        return self.band.GetNoDataValue()

    @property
    def xul(self):
        """ top lef x """
        return self.geo_transform[0]

    @property
    def yul(self):
        """ top lef y """
        return self.geo_transform[3]

    @property
    def cell_length(self):
        """ w-e pixel resolution """
        return self.geo_transform[1]

    @property
    def cell_height(self):
        """ n-s pixel resolution (negative value) """
        return self.geo_transform[5]

    @property
    def min(self):
        return self.band.GetMinimum()

    @property
    def max(self):
        return self.band.GetMaximum()

    @property
    def lats(self):
        step = abs(self.cell_height)
        start = self.yul - step / 2
        end = self.yul - step * self.rows
        return np.arange(start, end, -step)

    @property
    def lons(self):
        step = self.cell_length
        start = self.xul + step / 2
        end = self.xul + step * self.cols
        return np.arange(start, end, step)

    @classmethod
    def build(cls, pcr_map_filename):
        return cls(pcr_map_filename)


class PCRasterReader:

    FORMAT = 'PCRaster'
    digits = re.compile(r'\d+')

    def __init__(self, input_set):
        self.input_set = input_set
        self._driver = gdal.GetDriverByName(self.FORMAT)
        self._driver.Register()

    def get_metadata_from_set(self):
        """Get metadata from first map of set."""
        first_map, _ = next(self.fileset)
        return {'rows': first_map.rows, 'cols': first_map.cols,
                'lats': first_map.lats, 'lons': first_map.lons,
                'dtype': first_map.data.dtype}

    @property
    def fileset(self):
        if self.input_is_single_file():
            yield PCRasterMap.build(self.input_set), None
        elif self.input_is_wildcard():
            filelist = sorted(glob.glob(self.input_set), key=lambda x: self._extract_timestep(x))
            for f in filelist:
                yield PCRasterMap.build(f), self._extract_timestep(f)
        elif self.input_is_dir():
            filelist = sorted(os.listdir(self.input_set), key=lambda x: self._extract_timestep(x))
            for f in filelist:
                f = os.path.join(self.input_set, f)
                yield PCRasterMap.build(f), self._extract_timestep(f)
        else:
            raise ValueError('Cannot guess input PCRaster files')

    def input_is_single_file(self):
        return os.path.isfile(self.input_set)

    def input_is_wildcard(self):
        return '*' in self.input_set

    def input_is_dir(self):
        return os.path.isdir(self.input_set)

    @classmethod
    def _extract_timestep(cls, f):
        filename = os.path.basename(f).replace('.', '')
        try:
            step = cls.digits.findall(filename)[0]
        except IndexError:
            return None
        else:
            return int(step) - 1
