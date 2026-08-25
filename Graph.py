import matplotlib.pyplot as plt
import networkx as nx
from Meanders import Meander
from MarkovChain import PathCoupling


class MeanderGraph:
    def __init__(self, sample_space):
        self.sample_space = sample_space
        self.graph = nx.Graph()
        self.graph.add_nodes_from(sample_space.meanders)
        self._build_graph()

        self.worst_edge = None
        self.worst_case_value = None

        n = sample_space.n
        u_n = tuple(sorted((2 * i - 1, 2 * i) for i in range(1, n + 1)))
        l_n = tuple(sorted([(1, 2 * n)] + [(2 * i, 2 * i + 1) for i in range(1, n)]))

        m1 = Meander(top=u_n, bottom=l_n)
        m2 = Meander(top=l_n, bottom=u_n)

        self.special_nodes = {m for m in (m1, m2) if m in self.graph}

    def _is_obstructed(self, arc1, arc2, matching):
        i, j = sorted(arc1)
        k, l = sorted(arc2)
        if i > k:
            i, j, k, l = k, l, i, j

        for arc in matching:
            if arc == arc1 or arc == arc2:
                continue
            p, q = sorted(arc)

            cond1 = (i < j < p < k < l < q)
            cond2 = (i < p < k < l < q < j)
            cond3 = (p < i < j < q < k < l)

            if cond1 or cond2 or cond3:
                return True
        return False

    def get_unobstructed_pairs(self, matching):
        pairs = []
        n_arcs = len(matching)
        for idx1 in range(n_arcs):
            for idx2 in range(idx1 + 1, n_arcs):
                arc1 = matching[idx1]
                arc2 = matching[idx2]
                if not self._is_obstructed(arc1, arc2, matching):
                    pairs.append((arc1, arc2))
        return pairs

    def matching_exchange(self, matching, pair):
        arc1, arc2 = pair
        i, j = sorted(arc1)
        k, l = sorted(arc2)

        if i > k:
            i, j, k, l = k, l, i, j

        remaining = set(matching) - {arc1, arc2}

        if i < k and l < j:
            new_arcs = {(i, k), (j, l)}
        elif i < j and k < l and j < k:
            new_arcs = {(i, l), (j, k)}
        else:
            return None

        updated = list(remaining) + list(new_arcs)
        return tuple(sorted(tuple(sorted(a)) for a in updated))

    def _build_graph(self):
        meanders = self.sample_space.meanders

        for m in meanders:
            top_pairs = self.get_unobstructed_pairs(m.top)
            bottom_pairs = self.get_unobstructed_pairs(m.bottom)

            for p in top_pairs:
                new_top = self.matching_exchange(m.top, p)
                if new_top is None:
                    continue

                for q in bottom_pairs:
                    new_bottom = self.matching_exchange(m.bottom, q)
                    if new_bottom is None:
                        continue

                    if self.sample_space._is_valid_meander(new_top, new_bottom):
                        target = Meander(top=new_top, bottom=new_bottom)
                        if target in self.graph and target != m:
                            self.graph.add_edge(m, target)

    def _highlight_worst_edge(self):
        # just if its zero do nothing, trivial case
        if self.graph.number_of_edges() == 0:
            self.worst_edge = None
            self.worst_case_value = 0.0
            return

        pc = PathCoupling(self.graph)
        worst_case, worst_edge = pc.check_all_edges()
        self.worst_case_value = worst_case
        self.worst_edge = worst_edge

    def draw(self, highlight_worst=False):
        # Only calculate the worst edge if requested
        if highlight_worst:
            self._highlight_worst_edge()
        else:
            self.worst_edge = None
            self.worst_case_value = None

        fig, axes = plt.subplots(2, 2, figsize=(10, 8))
        (ax_main, ax_main_plot), (ax_sub, ax_sub_plot) = axes

        main_pos = nx.spring_layout(self.graph)
        main_meander_list = list(self.graph.nodes())
        n_main_nodes = len(main_meander_list)

        special_indices = {
            i
            for i, node in enumerate(main_meander_list)
            if node in self.special_nodes
        }

        main_nodes_artist = nx.draw_networkx_nodes(
            self.graph,
            main_pos,
            ax=ax_main,
            node_color=['white'] * n_main_nodes,
            edgecolors='black',
            linewidths=1.5,
            node_size=60,
        )
        main_nodes_artist.set_picker(True)

        # Edge colors based on whether highlight_worst was enabled
        main_edge_colors = [
            (
                'orange'
                if (
                        highlight_worst
                        and self.worst_edge
                        and set(edge) == {self.worst_edge[0], self.worst_edge[1]}
                )
                else 'black'
            )
            for edge in self.graph.edges()
        ]
        nx.draw_networkx_edges(
            self.graph, main_pos, ax=ax_main, edge_color=main_edge_colors
        )

        state = {
            'selected_main_idx': None,
            'selected_sub_idx': None,
            'sub_meander_list': [],
            'sub_pos': None,
            'sub_nodes_artist': None,
        }

        def update_visualization(recompute_sub_layout=False):
            ax_main_plot.clear()
            ax_sub.clear()
            ax_sub_plot.clear()

            colors_main = ['white'] * n_main_nodes
            for idx in special_indices:
                colors_main[idx] = 'magenta'

            if state['selected_main_idx'] is not None:
                selected_node = main_meander_list[state['selected_main_idx']]
                neighbors = set(self.graph.neighbors(selected_node))

                for idx, node in enumerate(main_meander_list):
                    if node in neighbors and idx not in special_indices:
                        colors_main[idx] = 'dodgerblue'

                colors_main[state['selected_main_idx']] = 'limegreen'

                sub_nodes_set = {selected_node} | neighbors
                subgraph = self.graph.subgraph(sub_nodes_set)
                state['sub_meander_list'] = list(subgraph.nodes())

                if recompute_sub_layout or state['sub_pos'] is None:
                    state['sub_pos'] = nx.spring_layout(subgraph)

                sub_colors = []
                for node in state['sub_meander_list']:
                    if (
                            state['selected_sub_idx'] is not None
                            and node == state['sub_meander_list'][state['selected_sub_idx']]
                    ):
                        sub_colors.append('red')
                    elif node == selected_node:
                        sub_colors.append('limegreen')
                    elif node in self.special_nodes:
                        sub_colors.append('magenta')
                    else:
                        sub_colors.append('dodgerblue')

                state['sub_nodes_artist'] = nx.draw_networkx_nodes(
                    subgraph,
                    state['sub_pos'],
                    ax=ax_sub,
                    node_color=sub_colors,
                    edgecolors='black',
                    linewidths=1.5,
                    node_size=80,
                )
                state['sub_nodes_artist'].set_picker(True)

                sub_edge_colors = [
                    (
                        'orange'
                        if (
                                highlight_worst
                                and self.worst_edge
                                and set(edge) == {self.worst_edge[0], self.worst_edge[1]}
                        )
                        else 'gray'
                    )
                    for edge in subgraph.edges()
                ]
                nx.draw_networkx_edges(
                    subgraph, state['sub_pos'], ax=ax_sub, edge_color=sub_edge_colors
                )

                if state['selected_sub_idx'] is not None:
                    sub_selected_node = state['sub_meander_list'][
                        state['selected_sub_idx']
                    ]
                    if sub_selected_node != selected_node:
                        main_red_idx = main_meander_list.index(sub_selected_node)
                        colors_main[main_red_idx] = 'red'

                    if sub_selected_node != selected_node:
                        top_move_arcs = set(selected_node.top) ^ set(sub_selected_node.top)
                        bottom_move_arcs = set(selected_node.bottom) ^ set(
                            sub_selected_node.bottom
                        )
                    else:
                        top_move_arcs, bottom_move_arcs = None, None

                    selected_node.plot(
                        ax=ax_main_plot,
                        top_move_arcs=top_move_arcs,
                        bottom_move_arcs=bottom_move_arcs,
                    )
                else:
                    selected_node.plot(ax=ax_main_plot)

                deg = self.graph.degree(selected_node)
                ax_main_plot.text(
                    0.95,
                    0.05,
                    f'Degree: {deg}',
                    transform=ax_main_plot.transAxes,
                    fontsize=12,
                    fontweight='bold',
                    ha='right',
                    va='bottom',
                )

                if state['selected_sub_idx'] is not None:
                    sub_selected_node = state['sub_meander_list'][
                        state['selected_sub_idx']
                    ]
                    sub_selected_node.plot(ax=ax_sub_plot)

                    sub_deg = self.graph.degree(sub_selected_node)
                    ax_sub_plot.text(
                        0.95,
                        0.05,
                        f'Degree: {sub_deg}',
                        transform=ax_sub_plot.transAxes,
                        fontsize=12,
                        fontweight='bold',
                        ha='right',
                        va='bottom',
                    )

            for ax in (ax_main, ax_main_plot, ax_sub, ax_sub_plot):
                ax.axis('off')

            main_nodes_artist.set_facecolor(colors_main)
            fig.canvas.draw_idle()

        update_visualization()

        def on_pick(event):
            if event.artist == main_nodes_artist:
                state['selected_main_idx'] = event.ind[0]
                state['selected_sub_idx'] = None
                update_visualization(recompute_sub_layout=True)

            elif (
                    state['sub_nodes_artist'] is not None
                    and event.artist == state['sub_nodes_artist']
            ):
                state['selected_sub_idx'] = event.ind[0]
                update_visualization(recompute_sub_layout=False)

        fig.canvas.mpl_connect('pick_event', on_pick)
        plt.tight_layout()
        plt.show(block=True)