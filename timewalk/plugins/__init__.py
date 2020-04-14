internal_plugin_info = [
    {
        "role": "lexer",
        "relative_import_name": ".lexer",
        "class_name": "TimeWalkLexer",
        "enabled": True
    },
    {
        "role": "adapter",
        "relative_import_name": ".adapter",
        "class_name": "SqliteAdapter",
        "enabled": True,
    },
    {
        "role": "formatter",
        "relative_import_name": ".formatter",
        "class_name": "JSONFormatter",
        "enabled": True,
    },
    {
        "role": "formatter",
        "relative_import_name": ".formatter",
        "class_name": "MarkdownReportFormatter",
        "enabled": True,
    },
    {
        "role": "general_plugin",
        "relative_import_name": ".plugins.duration",
        "class_name": "CoreDuration",
        "enabled": True,
    },
    {
        "role": "general_plugin",
        "relative_import_name": ".plugins.language",
        "class_name": "CoreLanguage",
        "enabled": True,
    },
    {
        "role": "general_plugin",
        "relative_import_name": ".plugins.project",
        "class_name": "CoreProject",
        "enabled": True
    },
    {
        "role": "general_plugin",
        "relative_import_name": ".plugins.invoker",
        "class_name": "CoreInvoker",
        "enabled": True,
    },
]
