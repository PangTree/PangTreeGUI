from .server import app
from .layout.css_styles import external_css
from .layout import layout

app.title = 'Poapangenome Visualisation'
app.layout = layout.get_layout(app.get_asset_url)
for css in external_css:
    app.css.append_css({"external_url": css})

from .callbacks import user_interactions
from .callbacks import broadcast_pangenome
# from .callbacks import parameters
from .callbacks import consensustable
from .callbacks import consensustree
# from .callbacks import multialignmentgraph
from .callbacks import mafgraph
from .callbacks import poagraph