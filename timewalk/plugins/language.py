from collections import defaultdict


class CoreLanguage():
    name = "core-language"
    version = (0, 0, 1)

    def __init__(self, args):
        pass

    def gather_heartbeat(self, ctx):
        ctx.current_heartbeat.update({
            "language": ctx.lexer.get_language()
        })

    def merge_heartbeats(self, ctx):
        info = self._combine_heartbeats(ctx.heartbeats)
        ctx.current_session.update(info)

    def write_report_section(self, ctx):
        items = []
        sessions = ctx.sessions

        lang_duration = self._combine_sessions(sessions)
        total_duration = sum(lang_duration.values())
        lang_time_percent = [
            (lang, dur, int(dur / total_duration * 10000) / 100)
            for lang, dur in sorted(lang_duration.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
        ]

        if len(lang_time_percent) > 0:
            items.append({
                "type": "literal",
                "content": "Check out your favourite language"
            })
            items.append({
                "type": "table",
                "header": ("Lang", "Seconds", "%"),
                "data": lang_time_percent
            })
        else:
            items.append({
                "type": "literal",
                "content": "No language data recorded"
            })

        ctx.report_sections.append(
            {
                "title": "Language - CoreLanguage",
                "items": items
            }
        )

    # def _duration_to_string(self, seconds):
    #     min, sec = divmod(seconds, 60)
    #     hr, min = divmod(min, 60)
    #     return "{} hr {} min {} sec".format(hr, min, sec)

    def _combine_heartbeats(self, heartbeats):
        result = defaultdict(int)
        for i in range(1, len(heartbeats)):
            if heartbeats[i].__contains__("language"):
                language_name = heartbeats[i]["language"]
                result[language_name] += heartbeats[i]["time"] - heartbeats[i - 1]["time"]

        return {
            "language": dict(result)
        }

    def _combine_sessions(self, sessions):
        result = defaultdict(int)
        lang_sessions = [sess["language"] for sess in sessions if sess.__contains__("language")]

        for sess in lang_sessions:
            for key, val in sess.items():
                result[key] += val

        return dict(result)
