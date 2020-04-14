from collections import defaultdict

class CoreProject():
    name = "core-project"
    version = (0, 0, 1)

    def __init__(self, args):
        self.args = args

    def gather_heartbeat(self, ctx):
        if ctx.args.__contains__("project") and ctx.args.project is not None:
            project = ctx.args.project
            ctx.current_heartbeat.update({
                "project": project
            })

    def merge_heartbeats(self, ctx):
        ctx.current_session.update(self._combine_heartbeats(ctx.heartbeats))

    def write_report_section(self, ctx):
        items = []
        sessions = ctx.sessions

        durs = self._combine_sessions(sessions)
        total_duration = sum(durs.values())
        project_time_percent = [
            (ivk, dur, int(dur / total_duration * 10000) / 100)
            for ivk, dur in sorted(durs.items(), key=lambda kv: kv[1], reverse=True)
        ]

        if len(project_time_percent) > 0:
            items.append({
                "type": "literal",
                "content": "Check out the projects you've been working on!".format(project_time_percent[0][0])
            })
            items.append({
                "type": "table",
                "header": ("Project", "Seconds", "%"),
                "data": project_time_percent
            })
        else:
            items.append({
                "type": "literal",
                "content": "No project data logged :("
            })

        ctx.report_sections.append(
            {
                "title": "Project - CoreProject",
                "items": items
            }
        )

    def _combine_heartbeats(self, hb):
        result = defaultdict(lambda: 0)
        for i in range(1, len(hb)):
            if hb[i].__contains__("project") and hb[i]["project"] is not None:
                invoker = hb[i]["project"]
                result[invoker] += hb[i]["time"] - hb[i - 1]["time"]

        return {
            "project": dict(result)
        }

    def _combine_sessions(self, sessions):
        result = defaultdict(int)
        project_sessions = [sess["project"] for sess in sessions if sess.__contains__("project")]

        for sess in project_sessions:
            for key, val in sess.items():
                result[key] += val

        return dict(result)
