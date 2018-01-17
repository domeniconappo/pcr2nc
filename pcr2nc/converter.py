"""

"""
from pcr2nc.reader import PCRasterReader
from pcr2nc.writer import NetCDFWriter


class Converter:

    def __init__(self, config):
        self.config = config
        input_set = config['input_set']
        self.reader = PCRasterReader(input_set)
        pcr_metadata = self.reader.get_metadata_from_set()
        self.writer = NetCDFWriter(config.get('output_filename') or config.get('variable'),
                                   config['metadata'],
                                   pcr_metadata, mapstack=not self.reader.input_is_single_file())

    def convert(self):
        for pcr_map, time_step in self.reader.fileset:
            self.writer.add_to_stack(pcr_map, time_step)
            pcr_map.close()
        self.writer.finalize()
