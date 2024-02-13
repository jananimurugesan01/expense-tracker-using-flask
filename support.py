import datetime
import pandas as pd
import sqlite3
import plotly
import plotly.express as px
import json
def connect_db():
    conn = sqlite3.connect("expense.db")
    cur = conn.cursor()
    cur.execute()
    cur.execute()
    conn.commit()
    return conn, cur
def close_db(connection=None, cursor=None):
    cursor.close()
    connection.close()
def execute_query(operation=None, query=None):
    connection, cursor = connect_db()
    if operation == 'search':
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        return data
    elif operation == 'insert':
        cursor.execute(query)
        connection.commit()
        cursor.close()
        connection.close()
        return None
def generate_df(df):
    df = df
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    df['Month_name'] = df['Date'].dt.month_name()
    df['Month'] = df['Date'].dt.month
    df['Day_name'] = df['Date'].dt.day_name()
    df['Day'] = df['Date'].dt.day
    df['Week'] = df['Date'].dt.isocalendar().week
    return df
def num2MB(num):
    if num < 1000:
        return int(num)
    if 1000 <= num < 1000000:
        return f'{float("%.2f" % (num / 1000))}K'
    elif 1000000 <= num < 1000000000:
        return f'{float("%.2f" % (num / 1000000))}M'
    else:
        return f'{float("%.2f" % (num / 1000000000))}B'
def top_tiles(df=None):
    if df is not None:
        tiles_data = df[['Expense', 'Amount']].groupby('Expense').sum()
        tiles = {'Earning': 0, 'Investment': 0, 'Saving': 0, 'Spend': 0}
        for i in list(tiles_data.index):
            try:
                tiles[i] = num2MB(tiles_data.loc[i][0])
            except:
                pass
        return tiles['Earning'], tiles['Spend'], tiles['Investment'], tiles['Saving']
    return
def generate_Graph(df=None):
    if df is not None and df.shape[0] > 0:
        # Bar_chart
        bar_data = df[['Expense', 'Amount']].groupby('Expense').sum().reset_index()
        bar = px.bar(x=bar_data['Expense'], y=bar_data['Amount'], color=bar_data['Expense'], template="plotly_dark",
                     labels={'x': 'Expense Type', 'y': 'Balance (₹)'}, height=287)
        bar.update(layout_showlegend=False)
        bar.update_layout(
            margin=dict(l=2, r=2, t=40, b=2),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)')
        # Stacked Bar Chart
        s = df.groupby(['Note', 'Expense']).sum().reset_index()
        stack = px.bar(x=s['Note'], y=s['Amount'], color=s['Expense'], barmode="stack", template="plotly_dark",
                       labels={'x': 'Category', 'y': 'Balance (₹)'}, height=290)
        stack.update(layout_showlegend=False)
        stack.update_xaxes(tickangle=45)
        stack.update_layout(
            margin=dict(l=2, r=2, t=30, b=2),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )

        # Line Chart
        line = px.line(df, x='Date', y='Amount', color='Expense', template="plotly_dark")
        line.update_xaxes(rangeslider_visible=True)
        line.update_layout(title_text='Track Record', title_x=0.,
                           legend=dict(
                               orientation="h",
                               yanchor="bottom",
                               y=1.02,
                               xanchor="right",
                               x=1
                           ),
                           margin=dict(l=2, r=2, t=30, b=2),
                           paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
                           )

        # Sunburst pie chart
        pie = px.sunburst(df, path=['Expense', 'Note'], values='Amount', height=280, template="plotly_dark")
        # pie.update_layout(title_text='Utility Chart', title_x=0.5)
        pie.update_layout(margin=dict(l=0, r=0, t=0, b=0),
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

        bar = json.dumps(bar, cls=plotly.utils.PlotlyJSONEncoder)
        pie = json.dumps(pie, cls=plotly.utils.PlotlyJSONEncoder)
        line = json.dumps(line, cls=plotly.utils.PlotlyJSONEncoder)
        stack_bar = json.dumps(stack, cls=plotly.utils.PlotlyJSONEncoder)

        return bar, pie, line, stack_bar
    return None
def makePieChart(df=None, expense='Earning', names='Note', values='Amount', hole=0.5,
                 color_discrete_sequence=px.colors.sequential.RdBu, size=300, textposition='inside',
                 textinfo='percent+label', margin=2):
    fig = px.pie(df[df['Expense'] == expense], names=names, values=values, hole=hole,
                 color_discrete_sequence=color_discrete_sequence, height=size, width=size)
    fig.update_traces(textposition=textposition, textinfo=textinfo)
    fig.update_layout(annotations=[dict(text=expense, y=0.5, font_size=20, font_color='white', showarrow=False)])
    fig.update_layout(margin=dict(l=margin, r=margin, t=margin, b=margin),
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig.update(layout_showlegend=False)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
def meraBarChart(df=None, x=None, y=None, color=None, x_label=None, y_label=None, height=None, width=None,
                 show_legend=False, show_xtick=True, show_ytick=True, x_tickangle=0, y_tickangle=0, barmode='relative'):
    bar = px.bar(data_frame=df, x=x, y=y, color=color, template="plotly_dark", barmode=barmode,
                 labels={'x': x_label, 'y': y_label}, height=height, width=width)
    bar.update(layout_showlegend=show_legend)
    bar.update_layout(
        margin=dict(l=2, r=2, t=2, b=2),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)')
    bar.update_layout(xaxis=dict(showticklabels=show_xtick, tickangle=x_tickangle),
                      yaxis=dict(showticklabels=show_ytick, tickangle=y_tickangle))
    return json.dumps(bar, cls=plotly.utils.PlotlyJSONEncoder)
def get_monthly_data(df, year=datetime.datetime.today().year, res='int'):
    temp = pd.DataFrame()
    d_year = df.groupby('Year').get_group(year)[['Expense', 'Amount', 'Month']]
    d_month = d_year.groupby("Month")
    for month in list(d_month.groups.keys())[::-1][:3]:
        dexp = d_month.get_group(month).groupby('Expense').sum().reset_index()
        for row in range(dexp.shape[0]):
            temp = temp.append(
                dict({"Expense": dexp.iloc[row]['Expense'], "Amount": dexp.iloc[row]['Amount'], "Month": month}),
                ignore_index=True)
    month_name = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: "July", 8: 'August',
                  9: "September", 10: "October", 11: "November", 12: "December"}
    ls = []
    for month in list(d_month.groups.keys())[::-1][:3]:
        m = {}
        s = temp[temp['Month'] == month]
        m['Month'] = month_name[month]
        for i in range(s.shape[0]):
            if res == 'int':
                m[s.iloc[i]['Expense']] = int(s.iloc[i]['Amount'])
            else:
                m[s.iloc[i]['Expense']] = num2MB(int(s.iloc[i]['Amount']))
        ls.append(m)
    return ls
def sort_summary(df):
    datas = []
    h_month, h_year, h_amount = [], [], []
    for year in list(df['Year'].unique()):
        d = df[df['Year'] == year]
        data = d[d['Expense'] == 'Earning'].groupby("Month_name").sum()['Amount'].reset_index().sort_values("Amount",
                                                                                                            ascending=False).iloc[
            0]
        h_month.append(data['Month_name'])
        h_year.append(year)
        h_amount.append(data['Amount'])
    amount = max(h_amount)
    month = h_month[h_amount.index(amount)]
    year = h_year[h_amount.index(amount)]
    datas.append(
        {'head': "₹" + str(num2MB(amount)), 'main': f"{month}'{str(year)[2:]}", 'msg': "Highest income in a month"})

    # per day avg income
    per_day_income = df[df['Expense'] == 'Earning']['Amount'].sum() / df['Date'].nunique()
    datas.append({'head': 'Income', 'main': "₹" + str(num2MB(per_day_income)), 'msg': "You earn everyday"})

    # per week avg spend
    per_week_saving = df[df['Expense'] == 'Saving'].groupby('Week').sum()['Amount'].mean()
    datas.append({'head': 'Saving', 'main': "₹" + str(num2MB(per_week_saving)), 'msg': "You save every week"})

    # per month income
    avg_earn = df[df['Expense'] == 'Earning'].groupby('Month').sum()['Amount'].reset_index()['Amount'].mean()
    # per month spend
    avg_spd = df[df['Expense'] == 'Spend'].groupby('Month').sum()['Amount'].reset_index()['Amount'].mean()

    # per month avg spend % wrt income
    monthly_spend = (avg_spd / avg_earn) * 100
    datas.append({'head': 'Spend', 'main': f"{round(monthly_spend, 2)}%", 'msg': "You spend every month"})

    # every minute invest
    every_minute_invest = round(df[df['Expense'] == 'Investment'].groupby('Day').sum()['Amount'].mean() / 24 / 60, 2)
    datas.append({'head': 'Invest', 'main': f"₹{round(every_minute_invest, 2)}", 'msg': "You invest every minute"})

    return datas


def expense_goal(df):
    """
    Monthly goal data
    :param df: Dataframe
    :return: list of dictionary
    """
    goal_ls = []
    for expense in list(df['Expense'].unique()):
        dic = {'type': expense}
        a = get_monthly_data(df, res='int')
        x = []
        for i in a[:2]:
            x.append(i[expense])
        first, second = x[0], x[1]
        diff = int(first) - int(second)
        percent = round((diff / second) * 100, 1)
        if percent > 0:
            dic['status'] = 'increased'
        else:
            dic['status'] = 'decreased'
        dic['percent'] = abs(percent)
        dic['value'] = "₹" + num2MB(x[0])
        goal_ls.append(dic)
    return goal_ls
