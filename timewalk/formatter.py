import json
import datetime
import logging

logger = logging.getLogger("TimeWalk")

class JSONFormatter():

    def __init__(self, args):
        self.args = args

    def format(self, data):
        return json.dumps(data)

class MarkdownReportFormatter():

    def __init__(self, args):
        self.args = args
        self.output = ""

    def _timestamp_to_string(self, timestamp):
        try:
            return datetime.datetime.fromtimestamp(timestamp).strftime("%b %d, %Y %H:%M:%S")
        except OSError:
            print("invalid timestamp", timestamp)
            return timestamp

    def format(self, sections):
        self._add_title(sections)
        self._add_core(sections)
        for section in sections:
            self._add_section(section)

        return self.output

    def _add_title(self, data):
        self._output_append("# TimeWalk Report\n")


    def _add_core(self, sections):
        start_time = self._timestamp_to_string(self.args.start_time)
        end_time = self._timestamp_to_string(self.args.end_time)
        self._output_append("{} - {}\n".format(start_time, end_time))



    def _add_section(self, section, level=2):
        self._output_append("{} {}\n".format("#" * level, section["title"]))
        for item in section["items"]:
            type = item.get("type", "")
            if type == "literal":
                self._output_append(item.get("content", ""))
            elif type == "data":
                self._output_append("{}: {}".format(item.get("description", ""), item.get("value", "")))
            elif type == "table":
                dscp = item.get("description", None)
                if dscp is not None:
                    self._output_append(dscp)
                table = self._markdown_table(item.get("header"), item.get("data"))
                self._output_append(table)
            elif type == "list":
                dscp = item.get("description", None)
                if dscp is not None:
                    self._output_append(dscp)
                lst = self._add_list(item.get("items"))
                self._output_append(lst)

            elif type == "subsection":
                self._add_section(item, level + 1)
            else:
                pass
        self._output_append("")

    def _output_append(self, string, buffer=None, indent=0):
        if buffer == None:
            self.output += " " * indent + str(string) + "\n"
            return self.output
        else:
            buffer += " " * indent + str(string) + "\n"
            return buffer


    def _add_list(self, list_items, indent=4):
        buffer = ""
        for item in list_items:
            type = item.get("type", "")
            if type == "literal":
                buffer = self._output_append("- " + item.get("content", ""), buffer, indent=indent)
            elif type == "data":
                buffer = self._output_append(
                    "{}: {}".format("- " + item.get("description", ""), item.get("value", "")), buffer, indent=indent)
            elif type == "list":
                dscp = item.get("description", None)
                if dscp:
                    buffer = self._output_append(dscp, buffer, indent=indent)
                self._add_list(item.get("items"), indent=indent+4)
        return buffer

    def _markdown_table(self, header, data):
        if len(data) == 0:
            logger.warning("No data provided for table formatting")
            return
        assert len(header) == len(data[0])
        arity = len(data[0])
        cardinality = len(data)

        width = [len(str(item)) for item in header]
        for i in range(cardinality):
            for j, item in enumerate(data[i]):
                width[j] = max(len(str(item)), width[j])

        formatted_header = "\n" + "| " + " | ".join(
            item.ljust(width[j]) for j, item in enumerate(header)) + " |" + "\n"
        formatted_header += "| " + "-|-".join("-" * width[j] for j in range(arity)) + " |" + "\n"
        content = "\n".join(
            "| " + " | ".join([str(item).ljust(width[j]) for j, item in enumerate(row)]) + " |"
            for row in data)
        return formatted_header + content + "\n"

