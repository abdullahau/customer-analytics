import altair as alt
import numpy as np

alt.renderers.enable('mimetype')

class ChartTemp(alt.Chart):
    def __init__(self, data, **kwargs):
        super().__init__(data=data, **kwargs)
    
    def line_encode(self, 
                    y_col, 
                    y_scale=alt.Scale(), 
                    y_title = 'Cumulative Sales (# Transactions)', 
                    dash=[1,0], 
                    color=alt.Color(), 
                    x_col='Week', 
                    x_title='Week', 
                    x_range=52):
        
        line = self.mark_line(strokeWidth=2, strokeDash=dash).encode(
            x = alt.X(x_col, 
                      scale=alt.Scale(domain=[0, x_range]),
                      axis = alt.Axis(
                          values=np.arange(0, x_range+1, 4),
                          labelExpr="datum.value",
                          title=x_title)
            ),
            y = alt.Y(y_col, 
                      title=y_title,
                      scale=y_scale
            ),
            color=color
        )
        return line   
    
    def line_prop(self, title):
        line = self.properties(
            width=650,
            height=250,
            title=title
        ).configure_view(stroke=None).configure_axisY(grid=False).configure_axisX(grid=False)     
        
        return line

def layered_line_prop(chart, title):
    line = chart.properties(
        width=650,
        height=250,
        title=title
    ).configure_view(stroke=None).configure_axisY(grid=False).configure_axisX(grid=False)     
    
    return line