class CoreDuration():
    name = "core-duration"
    version = (0, 0, 1)

    def __init__(self, args):
        self.args = args

    def write_report_section(self, ctx):
        items = []

        start_time, end_time = ctx.args.start_time, ctx.args.end_time
        total_duration = sum([sess["duration"] for sess in ctx.sessions])
        fraction = total_duration / (end_time - start_time)

        items.append(
            {
                "type": "list",
                "description": "In the given time period",
                "items": [
                    {
                        "type": "data",
                        "description": "Total coding time in second",
                        "value": total_duration,
                    },
                    {
                        "type": "data",
                        "description": "Fraction of your life spent in coding",
                        "value": round(fraction * 1000) / 1000,
                    }
                ],
            }
        )

        ctx.report_sections.append(
            {
                "title": "Core",
                "items": items,
            }
        )
