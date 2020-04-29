import json
import os
from pathlib import Path
from typing import Optional, List

from dataclasses import dataclass
from pygrok import Grok

import s3_log_shipper


class ParserManager:

    def __init__(self, config_file: Path, groks_dir=f'{os.path.dirname(s3_log_shipper.__file__)}/groks') -> None:
        self._config_file: Path = config_file

        with open(config_file.as_posix(), 'rb') as config_file:
            self._config: dict = json.load(config_file)

        if "files" not in self._config:
            raise ValueError("Config file format must contain top level \"files\" array")

        parsers: List[Parser] = list()
        for file in self._config['files']:
            parser: Parser = ParserManager.make_filter(file, groks_dir)
            parsers.append(parser)

        self._filters = parsers

    def __get__(self, obj, typ=None):
        return getattr(obj, self.name)

    @staticmethod
    def make_filter(file: dict, groks_dir):
        type: str = file['type']
        groks = [Grok(grok, custom_patterns_dir=groks_dir) for grok in file['path']]
        return Parser(Grok("%%{%s}" % type.upper(), custom_patterns_dir=groks_dir), groks)

    def get_parser(self, log_path: str):
        for flt in self._filters:
            match = flt.match_path(log_path)
            if match:
                return flt, match
        return None


@dataclass
class Parser:
    log_grok: Grok
    path_groks: List[Grok]

    def match_path(self, text) -> Optional[dict]:
        results = [grok.match(text) for grok in self.path_groks]

        if not any(results):
            return None

        dicts = [i for i in results if i]

        return {key: value for d in dicts for key, value in d.items()}

    def parse_log(self, log_entry) -> Optional[dict]:
        return self.log_grok.match(log_entry)
