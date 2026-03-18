import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

st.set_page_config(page_title="Trade Analytics", page_icon="✏️")

st.title("Explore your trade data with an interactive dashboard")

df = st.file_uploader("Upload your .xlsx file from MT5", type='xlsx')

try:
	df = pd.read_excel(df)

	# save account details to a different variable
	df_deets = df.iloc[:4].dropna(axis=1).reset_index(drop=True)
	df_deets = df_deets.rename(columns={'Unnamed: 3': ''})
	df_deets = df_deets.rename(columns={'Trade History Report': 'Account Details'})
	account_details, overview, metrics, positions = st.tabs(["Account Details", "Overview", "Metrics", "Position History"])

	account_balance = float(df.iloc[-37, 3])

	# Drop account details
	df = df.drop(index=df.index[:5]).reset_index(drop=True)

	# Find the first row where column 0 is not a valid datetime
	df_subset = df.iloc[1:]
	mask = pd.to_datetime(df_subset.iloc[:, 0], format='%Y.%m.%d %H:%M:%S', errors='coerce').isnull()
	first_text_row = df_subset[mask.values].index[0]

	# Keep only rows before that row
	df = df.loc[:first_text_row - 1]    

	df.columns = df.iloc[0]  
	df = df.drop(index=0).reset_index(drop=True)

	df = df.drop(columns=df.columns[-1])
	df.columns = ["Date Open",	"Position", "Symbol", "Type", "Volume",	"Open Price", "S/L Price", "T/P Price", 
					"Date Close", "Close Price", "Commission", "Swap", "PnL"]

	opendatetime = df['Date Open'].str.split(' ', expand=True)
	df['Date Open'] = opendatetime[0]
	df['Time Open'] = opendatetime[1]
	closedatetime = df['Date Close'].str.split(' ', expand=True)
	df['Date Close'] = closedatetime[0]
	df['Time Close'] = closedatetime[1]

	# moving columns
	df.insert(1, 'Time Open', df.pop('Time Open'))  
	df.insert(10, 'Time Close', df.pop('Time Close'))

	#reformating values from object to numbers and date times
	df[['Position', 'Volume', 'Open Price', 'S/L Price', 'T/P Price', 'Close Price', 'Commission', 'Swap', 
		'PnL']] = df[['Position', 'Volume', 'Open Price', 'S/L Price', 'T/P Price', 'Close Price',
						'Commission', 'Swap', 'PnL']].apply(pd.to_numeric, errors='coerce')

	df[['Date Open', 'Date Close']] = df[['Date Open', 'Date Close']].apply(
																			pd.to_datetime, format="%Y.%m.%d", 
																			errors='coerce').apply(lambda x: x.dt.date)
	#df[['Time Open', 'Time Close']] = df[["Time Open", 'Time Close']].apply(pd.to_datetime, format="%H:%M:%S", errors='coerce')

	pnl = df['PnL'].sum().round(2)
	totallots = df['Volume'].sum().round(2)
	totalswap = df['Swap'].sum().round(2)
	netpnl = pnl + totalswap
	account_size = account_balance - netpnl
	profit_pct = (netpnl/account_size)*100
	days = (df.iloc[-1]['Date Close'] - df.iloc[0]['Date Open']).days

	df['Current Balance'] = df['PnL'].cumsum() + account_size
	df.index = range(1, len(df) + 1)
	
	perdaypnl = df.pivot_table(values=['Volume', 'Swap', 'PnL'],
    							index='Date Close',
    							aggfunc='sum').reset_index()
	perdaypnl['Current Balance'] = perdaypnl['PnL'].cumsum() + account_size
	perdaypnl = perdaypnl.rename(columns={'Date Close': 'Date'})

	line_chart = px.line(perdaypnl, x='Date', y='Current Balance')
	y_min = perdaypnl['Current Balance'].min()
	y_max = perdaypnl['Current Balance'].max()
	lower = round(y_min * 0.98, -2)  
	upper = round(y_max * 1.02, -3)
	line_chart.update_yaxes(range=[lower, upper], tickformat=',.2f')

	with account_details:
		st.table(df_deets.set_index(pd.RangeIndex(start=1, stop=len(df_deets)+1)), border='horizontal')

	with positions:
		st.dataframe(df)

	with overview:
		acc_bal, days_traded, total_lot = st.columns(3)

		acc_bal.metric(label="Account Balance", value=f"${account_balance:,.2f}", 
						delta=f"{profit_pct.round(2)}%", border=True)
		days_traded.metric(label="Total Days Traded", value=days, delta="Calender days", 
							delta_color="grey", delta_arrow="off",  border=True)
		total_lot.metric(label="Total Volume", value=totallots, delta=f"Across {len(df)} trades", 
							delta_color="grey", delta_arrow="off", border=True)

		st.plotly_chart(line_chart)
		
except Exception as e:
    print(f"kuch toh galat hai: {e}")

