import sqlite3
import os
import pandas as pd
import streamlit as st

# اتصال به دیتابیس
conn = sqlite3.connect("c:/Users/barii/Desktop/nemoonekar/SabtDaramad2/finance.db")
c = conn.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = c.fetchall()
print("Tables:", tables)


# خواندن تراکنش‌ها
df = pd.read_sql_query("SELECT * FROM transactions", conn)

st.title("💸 داشبورد تراکنش‌ها")

# نمایش کل جدول
st.subheader("📋 همه تراکنش‌ها")
st.dataframe(df)

# آماری از درآمد، هزینه و مانده
st.subheader("📊 خلاصه وضعیت")

st.write('DataFrame Columns : ', df.columns.tolist())
st.dataframe(df)
income = df[df['t_type'] == 'income']['amount'].sum()
expense = df[df['t_type'] == 'expense']['amount'].sum()
balance = income - expense

st.metric("درآمد کل", f"{income:,.0f} تومان")
st.metric("هزینه کل", f"{expense:,.0f} تومان")
st.metric("مانده", f"{balance:,.0f} تومان")

# نمایش نمودار
st.subheader("📈 نمودار درآمد و هزینه")

chart_data = df.groupby(['t_type'])['amount'].sum().reset_index()
st.bar_chart(data=chart_data, x='t_type', y='amount')