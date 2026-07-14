"""
Implementation of the 'keywords' command
"""

from typing import TYPE_CHECKING

import networkx as nx

from robotframework_find_unused.commands.step.discover_files import step_discover_file_paths
from robotframework_find_unused.commands.step.keyword_count_uses import step_count_keyword_uses
from robotframework_find_unused.commands.step.keyword_definitions import (
    step_get_custom_keyword_definitions,
)
from robotframework_find_unused.commands.step.keyword_filter import step_filter_keywords
from robotframework_find_unused.commands.step.lib_keyword_definitions import (
    step_get_downloaded_lib_keywords,
)
from robotframework_find_unused.commands.step.parse_files import step_parse_files_with_libdoc

if TYPE_CHECKING:
    from robotframework_find_unused.common.const import KeywordData
    from robotframework_find_unused.reporter.base.keyword_reporter import KeywordReporter

    from .options import KeywordOptions


def command_keywords(options: "KeywordOptions", reporter: "KeywordReporter") -> None:
    """
    Entry point for the CLI command 'keywords'
    """
    reporter.on_command_start()

    file_paths = step_discover_file_paths(options.source_path, reporter=reporter)
    if file_paths is None:
        return

    files = step_parse_files_with_libdoc(file_paths, reporter=reporter)

    keywords = step_get_custom_keyword_definitions(files, reporter=reporter)
    if len(keywords) == 0 and options.library_keywords == "exclude":
        return

    downloaded_library_keywords = step_get_downloaded_lib_keywords(
        file_paths,
        reporter=reporter,
    )

    G = nx.DiGraph()
    for kw in keywords:
        G.add_node(kw.normalized_name)

    counted_keywords = step_count_keyword_uses(
        file_paths,
        keywords,
        downloaded_library_keywords,
        graph=G,
        reporter=reporter,
    )

    keywords_map: dict[str, KeywordData] = {}
    for kw in counted_keywords:
        keywords_map[kw.normalized_name] = kw

    for n in G.nodes:
        kw = keywords_map.get(n)
        if not kw:
            G.add_node(n, size=10, label=n, color="#993333")
            continue

        G.add_node(kw.normalized_name, size=kw.use_count * 20, label=kw.name, type=kw.type)

    # node_mass = {}
    # node_size = {}
    # for n in G.nodes:
    #     kw = keywords_map.get(n)
    #     if not kw:
    #         node_mass[n] = 1
    #         node_size[n] = 1
    #         continue

    #     node_mass[n] = kw.use_count * 20
    #     node_size[n] = kw.use_count * 20

    # G.remove_node("main")

    # nx.spring_layout(G, store_pos_as="pos")
    # nx.forceatlas2_layout(
    #     G,
    #     store_pos_as="pos",
    #     max_iter=1000,
    #     gravity=10,
    #     node_mass=node_mass,
    #     node_size=node_size,
    # )
    # nx.display(G)
    # gefx = nx.generate_gexf(G)
    # for l in nx.generate_gexf(G):
    #     print(l)
    with open("./tmp.gexf", "w+") as f:
        f.writelines(nx.generate_gexf(G))

    # plt.show()

    # counted_keywords = step_filter_keywords(counted_keywords, reporter=reporter)

    # reporter.on_command_end(counted_keywords)
