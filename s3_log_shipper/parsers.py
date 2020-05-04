import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple

from pygrok import Grok

import s3_log_shipper


@dataclass
class Parser:
    """
    Encapsulates the grok patterns to identify a specific log file and parse the logs within it.
    """

    type: str
    log_grok: Grok
    path_groks: List[Grok]
    strptime_pattern: str

    def match_path(self, log_path) -> Optional[dict]:
        """
        Attempts to match a log path using the path grok expressions
        :param log_path: the log path to test
        :return: A dictionary of the matches if any found, else None
        """
        results = [grok.match(log_path) for grok in self.path_groks]

        if not any(results):
            return None

        dicts = [i for i in results if i]

        return {key: value for d in dicts for key, value in d.items()}

    def parse_log(self, log_entry) -> Optional[dict]:
        """
        Attempts to parse the log entry using the log grok expression
        :param log_entry: the log entry to test
        :return: A dictionary of the matches if any found, else None
        """
        match = self.log_grok.match(log_entry)

        if "timestamp" in match:
            match["timestamp"] = datetime.strptime(
                match["timestamp"], self.strptime_pattern
            ).isoformat()

            # Rename for elasticsearch
            match["@timestamp"] = match.pop("timestamp")

        match["type"] = self.type

        return match


class ParserManager:
    """
    A class that builds a suite of parsers from a config file which are mapped onto particular log file paths,
    and encapsulate the logic to parse the useful information out of the entries in those log files.
    """

    def __init__(
        self,
        config_file: Path,
        groks_dir=f"{os.path.dirname(s3_log_shipper.__file__)}/groks",
    ) -> None:
        self._config_file: Path = config_file

        with open(config_file.as_posix(), "rb") as cf:
            self._config: dict = json.load(cf)

        if "files" not in self._config:
            raise ValueError('Config file format must contain top level "files" array.')

        parsers: List[Parser] = list()
        for file in self._config["files"]:
            parser: Parser = ParserManager.make_parser(file, groks_dir)
            parsers.append(parser)

        self._filters = parsers

    def __get__(self, obj, typ=None):
        return getattr(obj, self.name)

    @staticmethod
    def make_parser(file: dict, groks_dir) -> Parser:
        """
        Builds a parser from a config file entry and a directory of extra grok expressions.
        :param file: A single `file` element from the array within the config file.
        :param groks_dir: A directory to find additional grok patterns
        :return: A parser for the specified configuration
        """

        if not all(["type", "strptime", "path"] for key in file):
            raise ValueError(
                f"File entry requires 'type', 'strptime' and 'path' keys. Found:\n{file}"
            )

        type: str = file["type"]
        strptime_pattern: str = file["strptime"]
        groks = [Grok(grok, custom_patterns_dir=groks_dir) for grok in file["path"]]
        return Parser(
            type,
            Grok("%%{%s}" % type.upper(), custom_patterns_dir=groks_dir),
            groks,
            strptime_pattern,
        )

    def get_parser(self, log_path: str) -> Optional[Tuple[Parser, dict]]:
        """
        Retrieves a parser for a given log path
        :param log_path: The path to the log file
        :return: If a parser matches; A tuple of the parser and any matches from the path grok; else None
        """
        for flt in self._filters:
            match = flt.match_path(log_path)
            if match:
                return flt, match
        return None
