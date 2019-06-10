import plotly
import plotly.graph_objs as go

def an(x, y):
    return dict(
            x=x,
            y=y+0.2,
            showarrow=False,
            text=str(x),
        textangle=60
        )

x = [0, 1, 2, 3, 4]
x1 = [1, 1, 1, 1, 1]
x2 = [2, 2, 2, 2, 2]
x3 = [3, 3, 3, 3, 3]
y1 = [0.85, 0.72, 0.5, 0.3, 0.2]
y2 = [round(y**4, 3) for y in y1]
y3 = [round(y**0.25, 3) for y in y1]
m = dict(
            size = 10
          )
plotly.offline.plot({
    "data": [go.Scatter(x=y1, y=x1, mode='markers', name='P = 1', marker=m, text=y1, textposition='top center'),
             go.Scatter(x=[0.72], y=[1], mode='markers+text', marker=dict(size=20, color='rgba(0, 0, 0, 0.2)'), text=['PRÓG'], textposition='bottom center'),
             go.Scatter(x=y2, y=x2, mode='markers', name='P = 4', marker=m, text=y2, textposition='top center'),
             go.Scatter(x=[0.522], y=[2], mode='markers+text', marker=dict(size=20, color='rgba(0, 0, 0, 0.2)'), text=['PRÓG'], textposition='bottom center'),
             go.Scatter(x=y3, y=x3, mode='markers', name='P = 0.5', marker=m, text=y3, textposition='top center'),
             go.Scatter(x=[0.841], y=[3], mode='markers+text', marker=dict(size=20, color='rgba(0, 0, 0, 0.2)'), text=['PRÓG'], textposition='bottom center')],
    "layout": go.Layout(#title="Wyznaczanie progu zależne od parametru P",
                        showlegend=False,
                        xaxis=dict(
                            ticktext=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
                            tickvals=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
                            autorange=True,
                            showgrid=True,
                            zeroline=True,
                            showline=True,
                            ticks='',
                            showticklabels=True,
                        ),
                        yaxis=dict(
                            # autorange=True,
                            # showgrid=True,
                            # zeroline=True,
                            # showline=True,
                            ticktext=['P=1', 'P=4', 'P=0.25'],
                            tickvals=[1, 2, 3],
                            # showticklabels=False
                        ),
                        annotations=[an(x, y) for x, y in zip(y2, x2)]
                        + [an(x, y) for x, y in zip(y1, x1)] +
                            [an(x, y) for x, y in zip(y3, x3)]
                        )
}, auto_open=True)