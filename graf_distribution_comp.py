import plotly
import plotly.graph_objs as go
from plotly import tools
# def an(x, y):
#     return dict(
#             x=x,
#             y=y+0.2,
#             showarrow=False,
#             text=str(x),
#         textangle=60
#         )
#
# x = [0, 1, 2, 3, 4]
# x1 = [1, 1, 1, 1, 1]
# x2 = [2, 2, 2, 2, 2]
# x3 = [3, 3, 3, 3, 3]
# y1 = [0.9, 0.8, 0.7, 0.3, 0.2]
# y2 = [round(y**4, 3) for y in y1]
# y3 = [round(y**0.5, 3) for y in y1]
# m = dict(
#             size = 10
#           )
# plotly.offline.plot({
#     "data": [go.Scatter(x=y1, y=x1, mode='markers', name='P = 1', marker=m, text=y1, textposition='top center'),
#              go.Scatter(x=[0.7], y=[1], mode='markers+text', marker=dict(size=20, color='rgba(0, 0, 0, 0.2)'), text=['PRÓG'], textposition='bottom center'),
#              go.Scatter(x=y2, y=x2, mode='markers', name='P = 4', marker=m, text=y2, textposition='top center'),
#              go.Scatter(x=[0.6561], y=[2], mode='markers+text', marker=dict(size=20, color='rgba(0, 0, 0, 0.2)'), text=['PRÓG'], textposition='bottom center'),
#              go.Scatter(x=y3, y=x3, mode='markers', name='P = 0.5', marker=m, text=y3, textposition='top center'),
#              go.Scatter(x=[0.8367], y=[3], mode='markers+text', marker=dict(size=20, color='rgba(0, 0, 0, 0.2)'), text=['PRÓG'], textposition='bottom center')],
#     "layout": go.Layout(title="Wyznaczanie progu zależne od parametru P",
#                         showlegend=False,
#                         xaxis=dict(
#                             ticktext=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
#                             tickvals=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
#                             autorange=True,
#                             showgrid=True,
#                             zeroline=True,
#                             showline=True,
#                             ticks='',
#                             showticklabels=True,
#                         ),
#                         yaxis=dict(
#                             # autorange=True,
#                             # showgrid=True,
#                             # zeroline=True,
#                             # showline=True,
#                             ticktext=['P=1', 'P=4', 'P=0.5'],
#                             tickvals=[1, 2, 3],
#                             # showticklabels=False
#                         ),
#                         annotations=[an(x, y) for x, y in zip(y2, x2)]
#                         + [an(x, y) for x, y in zip(y1, x1)] +
#                             [an(x, y) for x, y in zip(y3, x3)]
#                         )
# }, auto_open=True)

trace1 = go.Scatter(
    x=[1, 2, 3],
    y=[4, 5, 6],
    mode='markers+text',
    text=['Text A', 'Text B', 'Text C'],
    textposition='bottom center'
)
trace2 = go.Scatter(
    x=[20, 30, 40],
    y=[50, 60, 70],
    mode='markers+text',
    text=['Text D', 'Text E', 'Text F'],
    textposition='bottom center'
)

fig = tools.make_subplots(rows=2, cols=1)

fig.append_trace(trace1, 1, 1)
fig.append_trace(trace2, 2, 1)
import matplotlib.pyplot as plt
import seaborn as sns
plt.figure()
max=[0.8612906644060613, 0.6806776071995765, 0.6585443711427963, 0.6357444561774023, 0.8549933774834437, 0.6823884389391773, 0.8554701986754967, 0.7997880794701987, 0.6421141559744443, 0.5871138104040138, 0.5871138104040138, 0.3434132049806425, 0.6375732615238396, 0.6373092560325255, 0.35382763853278215, 0.6794390050277851, 0.8613436473455547, 0.6378372670151539, 0.8641517431387093, 0.8612906644060613, 0.8121324503311258, 0.799841059602649, 0.8557350993377484, 0.6356916578669483, 0.6822152803515645, 0.6822152803515645, 0.6823884389391773, 0.6810121221745805, 0.6560310044595455, 0.8369801324503311]

node = [0.952951149729787, 0.5990471148755956, 0.5828367737816557, 0.5836325237592397, 0.9420397350993377, 0.5998094330633635, 0.9423576158940398, 0.8632582781456953, 0.5819737050530651, 0.5653023501452337, 0.5653023501452337, 0.3385999790729308, 0.5818153017582766, 0.5818681028565394, 0.3483857464287583, 0.5982005821645938, 0.9530041326692805, 0.5821321083478537, 0.9572427678287592, 0.952951149729787, 0.8783046357615895, 0.8629933774834437, 0.9426225165562914, 0.5835797254487857, 0.601471911897072, 0.6011542330703659, 0.5998094330633635, 0.5994388862421259, 0.5813336164790827, 0.9187814569536424]



# fig, axs = plt.subplots(2, 1)
ax = sns.kdeplot(node, shade=True, bw=.01)
ax = sns.distplot(node, rug=True, hist=False)

# ax.set_title(r'Rozkład wartości podobieństwa - konsensus ogólny')
ax.set_title(r'Rozkład wartości podobieństwa - konsensus szczegółowy')
plt.show()

# fig['layout'].update()
# plotly.offline.plot(fig, filename='simple-subplot-with-annotations')