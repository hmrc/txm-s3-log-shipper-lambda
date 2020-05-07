import csv
import json
import logging
import os
from pathlib import Path
from typing import Tuple
from unittest import TestCase

from s3_log_shipper.parsers import ParserManager, Parser
from test.fixtures import test_config_file

logging.basicConfig(level=logging.INFO)
logger: logging.Logger = logging.getLogger(__name__)


class LogParserSpec(TestCase):
    _config_file = Path(test_config_file()).absolute()

    def test_parse_no_exceptions(self):
        parser_manager = ParserManager(self._config_file)
        self.assertEqual(self._config_file, parser_manager._config_file)

    def test_parse_path_s3(self):
        parser_manager = ParserManager(self._config_file)

        path = (
            "bucket/emr-logs/j-2QN8WF3UJZKK3/node/i-0c08a7e99b9985c73/applications/oozie/oozie.log-2020-04-28"
            "-05.gz"
        )
        prs, match = parser_manager.get_parser(path)

        self.assertIsNotNone(prs)
        self.assertIsNotNone(match)

        self.assertEqual("bucket", match["bucketname"])
        self.assertEqual("j-2QN8WF3UJZKK3", match["cluster"])
        self.assertEqual("i-0c08a7e99b9985c73", match["node"])

    def test_parse_logs(self):
        parser_manager = ParserManager(self._config_file)

        with open(
            f"{os.path.dirname(__file__)}/sample_logs.csv", "rt"
        ) as sample_logs_file:
            for line in csv.reader(sample_logs_file, delimiter="|"):
                path = line[0]
                log = line[1]
                expected = json.loads(line[2])

                logger.info(path)

                pm: Tuple[Parser, dict] = parser_manager.get_parser(path)
                prs, path_groks = pm
                actual = prs.parse_log(log)
                actual.update(path_groks)

                self.assertEqual(
                    json.dumps(expected, sort_keys=True),
                    json.dumps(actual, sort_keys=True),
                )
