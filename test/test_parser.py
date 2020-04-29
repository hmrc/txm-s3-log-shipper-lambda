from datetime import datetime
from pathlib import Path
from typing import Tuple
from unittest import TestCase

from s3_log_shipper.parsers import (
    ParserManager,
    Parser)


class LogParserSpec(TestCase):
    _config_file = Path('./test_config.json').absolute()

    def test_parse_no_exceptions(self):
        parser_manager = ParserManager(self._config_file)
        self.assertEqual(self._config_file, parser_manager._config_file)

    def test_parse_path(self):
        parser_manager = ParserManager(self._config_file)

        path = "emr-logs/j-2QN8WF3UJZKK3/node/i-0c08a7e99b9985c73/applications/oozie/oozie.log-2020-04-28-05.gz"
        prs, match = parser_manager.get_parser(path)

        self.assertIsNotNone(prs)
        self.assertIsNotNone(match)

        self.assertEqual("j-2QN8WF3UJZKK3", match['cluster'])
        self.assertEqual("i-0c08a7e99b9985c73", match['node'])

    def test_parse_path_with_slash(self):
        parser_manager = ParserManager(self._config_file)

        path = "/emr-logs/j-2QN8WF3UJZKK3/node/i-0c08a7e99b9985c73/applications/oozie/oozie.log-2020-04-28-05.gz"
        prs, match = parser_manager.get_parser(path)

        self.assertIsNotNone(prs)
        self.assertIsNotNone(match)

        self.assertEqual("j-2QN8WF3UJZKK3", match['cluster'])
        self.assertEqual("i-0c08a7e99b9985c73", match['node'])

    def test_parse_path_s3(self):
        parser_manager = ParserManager(self._config_file)

        path = "s3://bucket/emr-logs/j-2QN8WF3UJZKK3/node/i-0c08a7e99b9985c73/applications/oozie/oozie.log-2020-04-28" \
               "-05.gz "
        prs, match = parser_manager.get_parser(path)

        self.assertIsNotNone(prs)
        self.assertIsNotNone(match)

        self.assertEqual("j-2QN8WF3UJZKK3", match['cluster'])
        self.assertEqual("i-0c08a7e99b9985c73", match['node'])

    def test_parse_log(self):
        parser_manager = ParserManager(self._config_file)

        path = "emr-logs/j-2QN8WF3UJZKK3/node/i-0c08a7e99b9985c73/applications/oozie/oozie.log-2020-04-28-05.gz "
        pm: Tuple[Parser, dict] = parser_manager.get_parser(path)

        prs = pm[0]

        match = prs.parse_log("".join(["2020-04-28 05:58:34,602  INFO StatusTransitService$StatusTransitRunnable:520 "
                                       "- SERVER[ip-10-202-31-224.eu-west-2.compute.internal] USER[-] GROUP[-] "
                                       "TOKEN[-] APP[-] JOB[-] ACTION[-] Released lock for ["
                                       "org.apache.oozie.service.StatusTransitService]"]))

        self.assertEqual(match['level'], 'INFO')
        self.assertEqual(match['message'], "".join(["StatusTransitService$StatusTransitRunnable:520 - SERVER["
                                                    "ip-10-202-31-224.eu-west-2.compute.internal] USER[-] GROUP[-] "
                                                    "TOKEN[-] APP[-] JOB[-] ACTION[-] Released lock for ["
                                                    "org.apache.oozie.service.StatusTransitService]"]))
        self.assertEqual(match['timestamp'], datetime.strptime("2020-04-28T05:58:34.602", "%Y-%m-%dT%H:%M:%S.%f"))
