import matplotlib.pyplot as plt
import matplotlib.patches as patches


class Meander:
    def __init__(self, top, bottom):
        self.top = tuple(sorted(tuple(sorted(arc)) for arc in top))  # sort list of tuples
        self.bottom = tuple(sorted(tuple(sorted(arc)) for arc in bottom))  # sort list of tuples
        self.num_points = len(self.top) * 2
        self.n = len(self.top)

    def plot(self, title=None, save_path=None, ax=None, top_move_arcs=None, bottom_move_arcs=None):
        show_at_end = False
        if ax is None:
            fig, ax = plt.subplots(figsize=(1.5 * self.n, 3))
            show_at_end = True

        x_coords = list(range(1, self.num_points + 1))

        ax.scatter(x_coords, [0] * self.num_points, color='black', zorder=5, s=30)
        for i in x_coords:
            ax.text(i - 0.1, -0.1, str(i), ha='right', va='center', fontsize=7)

        top_move_arcs = {tuple(sorted(arc)) for arc in top_move_arcs} if top_move_arcs else set()
        bottom_move_arcs = {tuple(sorted(arc)) for arc in bottom_move_arcs} if bottom_move_arcs else set()

        for u, v in self.top:
            center = (u + v) / 2.0
            width = abs(v - u)
            arc_key = (min(u, v), max(u, v))

            if arc_key in top_move_arcs:
                linestyle = '--'
                color = 'black'
                lw = 2.5
                zorder = 4
            else:
                linestyle = '-'
                color = 'black'
                lw = 2
                zorder = 3

            arc = patches.Arc((center, 0), width, width, angle=0,
                              theta1=0, theta2=180, color=color, lw=lw,
                              linestyle=linestyle, zorder=zorder)
            ax.add_patch(arc)

        # Draw bottom arcs
        for u, v in self.bottom:
            center = (u + v) / 2.0
            width = abs(v - u)
            arc_key = (min(u, v), max(u, v))

            if arc_key in bottom_move_arcs:
                linestyle = ':'
                color = 'black'
                lw = 2.5
                zorder = 4
            else:
                linestyle = '-'
                color = 'black'
                lw = 2
                zorder = 3

            arc = patches.Arc((center, 0), width, width, angle=0,
                              theta1=180, theta2=360, color=color, lw=lw,
                              linestyle=linestyle, zorder=zorder)
            ax.add_patch(arc)

        ax.set_xlim(0.5, self.num_points + 0.5)
        ax.set_ylim(-self.n, self.n)
        ax.set_aspect('equal')
        ax.axis('off')

        if title:
            ax.set_title(title)

        if save_path:
            plt.savefig(save_path, bbox_inches='tight')

        if show_at_end:
            plt.show()

    def __repr__(self):
        return f"Meander(n={self.n}, top={self.top}, bottom={self.bottom})"

    def __eq__(self, other):
        return isinstance(other, Meander) and self.top == other.top and self.bottom == other.bottom

    def __hash__(self):
        return hash((self.top, self.bottom))


