from collections import defaultdict


class CoreInvoker():
    name = "core-invoker"
    version = (0, 0, 1)

    def __init__(self, args):
        self.args = args

    def gather_heartbeat(self, ctx):
        if ctx.args.__contains__("invoker") and ctx.args.invoker is not None:
            editor = ctx.args.invoker.split("/")[0]
            ctx.current_heartbeat.update({
                "invoker": editor
            })

    def merge_heartbeats(self, ctx):
        ctx.current_session.update(self._combine_heartbeats(ctx.heartbeats))

    def write_report_section(self, ctx):
        items = []
        sessions = ctx.sessions

        invoker_dur = self._combine_sessions(sessions)
        total_duration = sum(invoker_dur.values())
        invoker_time_percent = [
            (ivk, dur, int(dur / total_duration * 10000) / 100)
            for ivk, dur in sorted(invoker_dur.items(), key=lambda kv: kv[1], reverse=True)
        ]

        if len(invoker_time_percent) > 0:
            items.append({
                "type": "literal",
                "content": "Your fav editor is {}!".format(invoker_time_percent[0][0])
            })
            items.append({
                "type": "table",
                "header": ("Editor", "Seconds", "%"),
                "data": invoker_time_percent
            })
        else:
            items.append({
                "type": "literal",
                "content": "No editor data recorded :("
            })

        ctx.report_sections.append(
            {
                "title": "Editor - CoreInvoker",
                "items": items
            }
        )

    def _combine_heartbeats(self, hb):
        result = defaultdict(lambda: 0)
        for i in range(1, len(hb)):
            if hb[i].__contains__("invoker") and hb[i]["invoker"] is not None:
                invoker = hb[i]["invoker"]
                result[invoker] += hb[i]["time"] - hb[i - 1]["time"]

        return {
            "invoker": dict(result)
        }

    def _combine_sessions(self, sessions):
        result = defaultdict(int)
        invoker_sessions = [sess["invoker"] for sess in sessions if sess.__contains__("invoker")]

        for sess in invoker_sessions:
            for key, val in sess.items():
                result[key] += val

        return dict(result)
