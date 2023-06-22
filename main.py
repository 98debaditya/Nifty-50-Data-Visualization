import dash
import dash_bootstrap_components as dbc
from dash import html, ctx
from dash import dcc
import plotly.graph_objects as go
import pandas as pd
from datetime import date
import numpy as np
from dash.dependencies import Input, Output, State
import DataBase as DB

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    external_stylesheets=[dbc.themes.CYBORG],
)

server = app.server

app.layout = dbc.Container(
    children=[
        dbc.Row(
            [   
                dbc.Col(
                    [
                        html.Br(),
                        dbc.ButtonGroup(
                            [
                                dbc.Button("Refresh Data", id="refresh-button"),
                                html.Div(id="output-div"),
                                dcc.DatePickerSingle(
                                    id='start',
                                    min_date_allowed='2020-10-01',
                                    max_date_allowed='2023-12-31',
                                    initial_visible_month='2021-10-01'
                                ),html.Div(id="startd"),
                                dcc.DatePickerSingle(
                                    id='end',
                                    min_date_allowed='2020-10-01',
                                    max_date_allowed='2023-12-31',
                                    initial_visible_month='2023-01-01'
                                ),html.Div(id="endd"),
                                dcc.Input(id='nn',type='number',value=10,min=1,max=50),
                                html.Div(id='nshow'),
                                dcc.Input(id='invs',type='number',value=1000000,min=10000,),
                                html.Div(id='invsw'),
                            ],
                            vertical=True,
                            className="d-grid gap-2"
                        ),
                        html.Br(),
                        html.Div(children="Performance Matrix"),
                        html.Div(id="table-container"),
                    ],
                    width={"size": 2, "offset": 0}
                ),
                dbc.Col(
                    dcc.Graph(id = 'main',figure=go.Figure()),
                ),
            ],
            style={"height": "850px"}
        ),
    ],
    fluid=True,
)

@app.callback(Output("output-div", "children"),
              Output("startd", "children"),
              Output("endd", "children"),
              Output('main', 'figure'),
              Output('nshow', 'children'),
              Output('invsw', 'children'),
              Output("table-container", "children"),
              [Input("refresh-button", "n_clicks"),
              Input("start", "date"),
              Input("end", "date"),
              Input("nn", "value"),
              Input("invs", "value")])
def button_click(n_clicks,sdate,eday,nn,invs):
        if invs == None:
            invs = 10000
        else:
            pass
        if nn == None:
                nn = 1
        else:
            pass
        if 'refresh-button' == ctx.triggered_id:
            DB.UpdateData()
        dff = pd.read_csv('Nifty.csv')
        inv = invs/50
        num = dff.iloc[:, 1:].iloc[0]
        num = inv/num
        num = num.astype(int)
        eqt = dff.iloc[:, 1:]
        eqt = eqt.multiply(num, axis=1)
        eqt = eqt.sum(axis = 1)
        df = pd.DataFrame()
        df['DATE'] = dff['DATE']
        df['SUM'] = eqt
        inv1 = invs/nn
        eqt1 = dff.iloc[:, 1:]
        eqt1 = eqt1.iloc[:, :nn]
        num1 = eqt1.iloc[0]
        num1 = inv1/num1
        num1 = num1.astype(int)
        eqt1 = eqt1.multiply(num1, axis=1)
        eqt1 = eqt1.sum(axis = 1)
        df1 = pd.DataFrame()
        df1['DATE'] = dff['DATE']
        df1['SUM'] = eqt1
        dff2 = pd.read_csv('NiftyIndex.csv')
        num = dff2.iloc[0]
        num = invs/num
        num = num.astype(int)
        dff2 = dff2.multiply(num, axis=1)
        if sdate is None and eday is None:
            figure =go.Figure(data=[go.Scatter(x=df['DATE'], y=df['SUM'], mode='lines', name='Equal Strategy', line=dict(color='yellow')),
                                    go.Scatter(x=df1['DATE'], y=df1['SUM'], mode='lines', name=f'Top {nn} Shares', line=dict(color='green')),
                                    go.Scatter(x=df1['DATE'], y=dff2['Close'], mode='lines', name='Nifty Index', line=dict(color='red'))],
                            layout=go.Layout(
                                title=f'Equity Curves of Nifty index, Equal and the Sample strategy (Top {nn} Shares)',
                                showlegend=True,
                                xaxis=dict(title='DATE'),
                                yaxis=dict(title='EQUITY'),
                                template='plotly_dark',
                                height=719,
                                width=850,
                            )
                        )
            t = df.shape[0]/252
            caga1 = (((df['SUM'].iloc[-1]/df['SUM'].iloc[0])**(1/t)-1)*100).round(2)
            caga2 = (((df1['SUM'].iloc[-1]/df1['SUM'].iloc[0])**(1/t)-1)*100).round(2)
            caga3 = (((dff2['Close'].iloc[-1]/dff2['Close'].iloc[0])**(1/t)-1)*100).round(2)
            dr1 = ((df['SUM'] / df['SUM'].shift(1)) - 1).fillna(0)
            sd1 = dr1.std()
            mean1 = dr1.mean()
            srp1 = ((mean1/sd1)**(1/252)).round(2)
            vlt1 = ((sd1**(1/252))*100).round(2)
            dr2 = ((df1['SUM']/df1['SUM'].shift(1)) - 1).fillna(0)
            sd2 = dr2.std()
            mean2 = dr2.mean()
            srp2 = ((mean2/sd2)**(1/252)).round(2)
            vlt2 = ((sd2**(1/252))*100).round(2)
            dr3 = ((dff2['Close']/dff2['Close'].shift(1))-1).fillna(0)
            sd3 = dr3.std()
            mean3 = dr3.mean()
            srp3 = ((mean3/sd3)**(1/252)).round(2)
            vlt3 = ((sd3**(1/252))*100).round(2)
            dfr = pd.DataFrame({'Index': ['Equal Strategy', 'Nifty Index', f'Top {nn} Shares'], 'CAGR %': [caga1, caga2, caga3], 'Volatility %' :[vlt1 , vlt2 , vlt3],'Sharpe Ratio' :[srp1, srp2, srp3]})
            table = dbc.Table.from_dataframe(dfr, striped=True, bordered=True, hover=True)
            return 'This May Take Some Time','Start Day','End Day', figure, f'Top {nn} Shares','Investment',table
        if sdate is not None and eday is None:
            df = df[df['DATE'].apply(lambda x: x >= sdate)]
            df1 = df1[df1['DATE'].apply(lambda x: x >= sdate)]
            figure =go.Figure(data=[go.Scatter(x=df['DATE'], y=df['SUM'], mode='lines', name='Equal Strategy', line=dict(color='yellow')),
                                    go.Scatter(x=df1['DATE'], y=df1['SUM'], mode='lines', name=f'Top {nn} Shares', line=dict(color='green')),
                                    go.Scatter(x=df1['DATE'], y=dff2['Close'], mode='lines', name='Nifty Index', line=dict(color='red'))],
                            layout=go.Layout(
                                title=f'Equity Curves of Nifty index, Equal and the Sample strategy (Top {nn} Shares)',
                                showlegend=True,
                                xaxis=dict(title='DATE'),
                                yaxis=dict(title='EQUITY'),
                                template='plotly_dark',
                                height=719,
                                width=850
                            )
                        )
            t = df.shape[0]/252
            caga1 = (((df['SUM'].iloc[-1]/df['SUM'].iloc[0])**(1/t)-1)*100).round(2)
            caga2 = (((df1['SUM'].iloc[-1]/df1['SUM'].iloc[0])**(1/t)-1)*100).round(2)
            caga3 = (((dff2['Close'].iloc[-1]/dff2['Close'].iloc[0])**(1/t)-1)*100).round(2)
            dr1 = ((df['SUM'] / df['SUM'].shift(1)) - 1).fillna(0)
            sd1 = dr1.std()
            mean1 = dr1.mean()
            srp1 = ((mean1/sd1)**(1/252)).round(2)
            vlt1 = ((sd1**(1/252))*100).round(2)
            dr2 = ((df1['SUM']/df1['SUM'].shift(1)) - 1).fillna(0)
            sd2 = dr2.std()
            mean2 = dr2.mean()
            srp2 = ((mean2/sd2)**(1/252)).round(2)
            vlt2 = ((sd2**(1/252))*100).round(2)
            dr3 = ((dff2['Close']/dff2['Close'].shift(1))-1).fillna(0)
            sd3 = dr3.std()
            mean3 = dr3.mean()
            srp3 = ((mean3/sd3)**(1/252)).round(2)
            vlt3 = ((sd3**(1/252))*100).round(2)
            dfr = pd.DataFrame({'Index': ['Equal Strategy', 'Nifty Index', f'Top {nn} Shares'], 'CAGR %': [caga1, caga2, caga3], 'Volatility %' :[vlt1 , vlt2 , vlt3],'Sharpe Ratio' :[srp1, srp2, srp3]})
            table = dbc.Table.from_dataframe(dfr, striped=True, bordered=True, hover=True)
            return 'This May Take Some Time',sdate,'End Day', figure, f'Top {nn} shares', 'Investment',table
        if sdate is None and eday is not None:
            df = df[df['DATE'].apply(lambda x: x <= eday)]
            df1 = df1[df1['DATE'].apply(lambda x: x <= eday)]
            figure =go.Figure(data=[go.Scatter(x=df['DATE'], y=df['SUM'], mode='lines', name='Equal Strategy', line=dict(color='yellow')),
                                    go.Scatter(x=df1['DATE'], y=df1['SUM'], mode='lines', name=f'Top {nn} Shares', line=dict(color='green')),
                                    go.Scatter(x=df1['DATE'], y=dff2['Close'], mode='lines', name='Nifty Index', line=dict(color='red'))],
                            layout=go.Layout(
                                title=f'Equity Curves of Nifty index, Equal and the Sample strategy (Top {nn} Shares)',
                                showlegend=True,
                                xaxis=dict(title='DATE'),
                                yaxis=dict(title='EQUITY'),
                                template='plotly_dark',
                                height=719,
                                width=850
                            )
                        )
            t = df.shape[0]/252
            caga1 = (((df['SUM'].iloc[-1]/df['SUM'].iloc[0])**(1/t)-1)*100).round(2)
            caga2 = (((df1['SUM'].iloc[-1]/df1['SUM'].iloc[0])**(1/t)-1)*100).round(2)
            caga3 = (((dff2['Close'].iloc[-1]/dff2['Close'].iloc[0])**(1/t)-1)*100).round(2)
            dr1 = ((df['SUM'] / df['SUM'].shift(1)) - 1).fillna(0)
            sd1 = dr1.std()
            mean1 = dr1.mean()
            srp1 = ((mean1/sd1)**(1/252)).round(2)
            vlt1 = ((sd1**(1/252))*100).round(2)
            dr2 = ((df1['SUM']/df1['SUM'].shift(1)) - 1).fillna(0)
            sd2 = dr2.std()
            mean2 = dr2.mean()
            srp2 = ((mean2/sd2)**(1/252)).round(2)
            vlt2 = ((sd2**(1/252))*100).round(2)
            dr3 = ((dff2['Close']/dff2['Close'].shift(1))-1).fillna(0)
            sd3 = dr3.std()
            mean3 = dr3.mean()
            srp3 = ((mean3/sd3)**(1/252)).round(2)
            vlt3 = ((sd3**(1/252))*100).round(2)
            dfr = pd.DataFrame({'Index': ['Equal Strategy', 'Nifty Index', f'Top {nn} Shares'], 'CAGR %': [caga1, caga2, caga3], 'Volatility %' :[vlt1 , vlt2 , vlt3],'Sharpe Ratio' :[srp1, srp2, srp3]})
            table = dbc.Table.from_dataframe(dfr, striped=True, bordered=True, hover=True)
            return 'This May Take Some Time' ,'Start Date', eday , figure, f'Top {nn} Shares', 'Investment',table
        if sdate is not None and eday is not None:
            df = df[df['DATE'].apply(lambda x: x <= eday)]
            df = df[df['DATE'].apply(lambda x: x >= sdate)]
            df1 = df1[df1['DATE'].apply(lambda x: x <= eday)]
            df1 = df1[df1['DATE'].apply(lambda x: x >= sdate)]
            figure =go.Figure(data=[go.Scatter(x=df['DATE'], y=df['SUM'], mode='lines', name='Equal Strategy', line=dict(color='yellow'),),
                                    go.Scatter(x=df1['DATE'], y=df1['SUM'], mode='lines', name=f'Top {nn} Shares', line=dict(color='green')),
                                    go.Scatter(x=df1['DATE'], y=dff2['Close'], mode='lines', name='Nifty Index', line=dict(color='red'))],
                            layout=go.Layout(
                                title=f'Equity Curves of Nifty index, Equal and the Sample strategy (Top {nn} Shares)',
                                showlegend=True,
                                xaxis=dict(title='DATE'),
                                yaxis=dict(title='EQUITY'),
                                template='plotly_dark',
                                height=719,
                                width=850,
                            )
                        )
            t = df.shape[0]/252
            caga1 = (((df['SUM'].iloc[-1]/df['SUM'].iloc[0])**(1/t)-1)*100).round(2)
            caga2 = (((df1['SUM'].iloc[-1]/df1['SUM'].iloc[0])**(1/t)-1)*100).round(2)
            caga3 = (((dff2['Close'].iloc[-1]/dff2['Close'].iloc[0])**(1/t)-1)*100).round(2)
            dr1 = ((df['SUM'] / df['SUM'].shift(1)) - 1).fillna(0)
            sd1 = dr1.std()
            mean1 = dr1.mean()
            srp1 = ((mean1/sd1)**(1/252)).round(2)
            vlt1 = ((sd1**(1/252))*100).round(2)
            dr2 = ((df1['SUM']/df1['SUM'].shift(1)) - 1).fillna(0)
            sd2 = dr2.std()
            mean2 = dr2.mean()
            srp2 = ((mean2/sd2)**(1/252)).round(2)
            vlt2 = ((sd2**(1/252))*100).round(2)
            dr3 = ((dff2['Close']/dff2['Close'].shift(1))-1).fillna(0)
            sd3 = dr3.std()
            mean3 = dr3.mean()
            srp3 = ((mean3/sd3)**(1/252)).round(2)
            vlt3 = ((sd3**(1/252))*100).round(2)
            dfr = pd.DataFrame({'Index': ['Equal Strategy', 'Nifty Index', f'Top {nn} shares'], 'CAGR %': [caga1, caga2, caga3], 'Volatility %' :[vlt1 , vlt2 , vlt3],'Sharpe Ratio' :[srp1, srp2, srp3]})
            table = dbc.Table.from_dataframe(dfr, striped=True, bordered=True, hover=True)
            return 'This May Take Some Time' , sdate , eday , figure, f'Top {nn} Shares', 'Investment',table

if __name__ == "__main__":
    app.run_server(debug=True)
