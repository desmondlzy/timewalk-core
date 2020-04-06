from datetime import timedelta
from .utils import TestCase, MockedNamespace, TestingDB
from testfixtures import TempDirectory

from timewalk.formatter import JSONFormatter, MarkdownReportFormatter
from timewalk.plugins.language import CoreLanguage
from timewalk.plugins.duration import CoreDuration


class TestFormatter(TestCase):

    def test_markdown_formatter(self):
        pivot = 10 ** 9

        def delta(**kwargs):
            return int(timedelta(**kwargs).total_seconds())

        args = MockedNamespace({
            "start_time": pivot - delta(days=7),
            "end_time": pivot,
        })
        formatter = MarkdownReportFormatter(args)
        dur_plugin = CoreDuration(args)
        lang_plugin = CoreLanguage(args)

        sessions = [
            {
                "start": pivot - delta(days=6, hours=20),
                "end": pivot - delta(days=6, hours=19),
                "duration": delta(hours=1),
                "language": {
                    "Python": delta(minutes=20),
                    "C": delta(minutes=20),
                }
            },
            {
                "start": pivot - delta(days=5, hours=20),
                "end": pivot - delta(days=5, hours=19),
                "duration": delta(hours=1),
                "language": {
                    "Go": delta(minutes=20),
                    "C": delta(minutes=20),
                }
            },
            {
                "start": pivot - delta(days=4, hours=17),
                "end": pivot - delta(days=4, hours=16),
                "duration": delta(hours=1),
                "language": {
                    "C++": delta(minutes=20),
                    "C": delta(minutes=20),
                }
            },
        ]

        context = MockedNamespace({
            "args": args,
            "sessions": sessions,
            "report_sections": []
        })

        dur_plugin.write_report_section(context)
        lang_plugin.write_report_section(context)
        expected = [
            {
                'title': 'Core',
                'items': [
                    {
                        'type': 'list',
                        'description': 'In the given time period',
                        'items': [
                            {'type': 'data', 'description': 'Total coding time in second', 'value': 10800},
                            {'type': 'data', 'description': 'Fraction of your life spent in coding', 'value': 0.018}
                        ]
                    }
                ]
            },
            {
                'title': 'Language - CoreLanguage',
                'items': [
                    {
                        'type': 'literal',
                        "content": "Stats of your languages usage",
                    },
                    {
                        'type': 'table',
                        'header': ('Lang', 'Seconds', '%'),
                        'data': [
                            ('C', 3600, 50.0),
                            ('Python', 1200, 16.66),
                            ('Go', 1200, 16.66),
                            ('C++', 1200, 16.66)
                        ]
                    }
                ]
            }
        ]
        self.assertListEqual(context.report_sections, expected)
        output = formatter.format(context.report_sections)
        with open("./tests/samples/output/test_formatter_output.txt", "r") as f:
            self.assertEqual(output, f.read())
