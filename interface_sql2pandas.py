# -*- coding: utf-8 -*-


# streamlit_app.py
"""interface_sql2pandas.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1FRPmPH4y24A0vxSuqqQa6ZBOR1NU6C9U
"""

# Import libraries
import mysql.connector
import pandas as pd
import streamlit as st
import getpass
import seaborn as sn
from matplotlib import pyplot as plt

sn.set_palette(palette= "Set2")

links = ["<a href='#Logistic'>Logistic</a>",\
         "<a href='#Finances'>Finances </a>",\
         #"<a href='#finances-2'>Finances 2</a>",\
         "<a href='#Sales'>Sales</a>",\
         "<a href='#Human-Resources'>Human Resources</a>"]
for l in links:
    st.sidebar.write(
        l,
        unsafe_allow_html=True
    )

# Connection with public password
connection = mysql.connector.connect(**st.secrets["mysql"])
#query = "SELECT * from orders WHERE orderDate like '2022-02%'"

"""## Logistic
    The stock of the 5 most ordered products
"""

# \ to go to the new line if the code is too long
query_logistic = \
  "SELECT o.productCode, \
    p.productName, \
    p.productLine, \
    SUM(o.quantityOrdered) as qty_ordered, \
    p.quantityInStock as available_qty \
  FROM orderdetails as o\
  JOIN products as p ON p.productCode = o.productCode\
  GROUP BY p.productCode\
  ORDER BY SUM(o.quantityOrdered) DESC\
  LIMIT 5;"

# Add names of the product
# sql to pandas
df_logistic = pd.read_sql_query(query_logistic, con = connection)
df_logistic['qty_ordered'] = df_logistic['qty_ordered'].astype('int')
df_logistic.index = df_logistic.index + 1
df_logistic
#st.write(df_logistic.style.hide_index().to_html() + "<br>",unsafe_allow_html=True)

# Set plot
fig1, ax1 = plt.subplots()
df_logistic.set_index("productCode").plot(kind="bar", \
                 title="The stock of the 5 most ordered products.",\
                 xlabel="Product code",\
                 rot=0,\
                 ax = ax1,\
                 ylabel="Quantity").legend(["Ordered", "Available"])

st.pyplot(fig1)

"""## Finances
    The turnover of the orders of the last two months by country
"""

query_finance_one = \
"SELECT \
    c.country, \
    SUM(od.quantityOrdered * od.priceEach) as turnover \
FROM orders AS o \
JOIN customers as c \
ON c.customerNumber = o.customerNumber \
JOIN orderdetails as od \
ON od.orderNumber = o.orderNumber \
WHERE MONTH(o.shippedDate) >= MONTH(NOW() - INTERVAL 2 MONTH) AND YEAR(o.shippedDate) = YEAR(NOW()) \
GROUP BY c.country \
ORDER BY turnover DESC ;"

# Reorganise the display
# sql to pandas
df_finance1 = pd.read_sql_query(query_finance_one, con = connection)
df_finance1.rename(columns = {"turnover": "turnover (€)"}, inplace= True)
df_finance1.index = df_finance1.index + 1
df_finance1

#create the bar chart
fig3, ax3 = plt.subplots()
#df_finance1.barplot(x="country", \
#                     y="turnover (€)", \
#                     title= "The turnover of the orders in the last two months, by country", \
#                     ylabel= "turnover (€)", \
#                     legend = False,\
#                     figsize= (10, 3),\
#                     ax=ax3)
sn.barplot(y="country", x="turnover (€)", data=df_finance1, ax=ax3)
st.pyplot(fig3)

st.code("Orders that haven't yet been paid.")

query_finance_two = \
'WITH sub_order AS (\
SELECT \
	o.customerNumber, \
	o.orderNumber, \
	SUM(DISTINCT od.quantityOrdered * od.priceEach) as amount_order \
FROM orders AS o \
LEFT JOIN orderdetails as od ON od.orderNumber = o.orderNumber \
GROUP BY o.orderNumber \
) \
SELECT * FROM orders \
WHERE orderNumber IN ( \
SELECT o.orderNumber FROM sub_order as o \
JOIN payments as p ON p.customerNumber = o.customerNumber \
WHERE p.amount < o.amount_order) \
AND NOT status = "cancelled";' \

# sql to pandas
df_finance2 = pd.read_sql_query(query_finance_two, con = connection)
df_finance2['year'] = pd.DatetimeIndex(df_finance2['orderDate']).year
df_finance2['month'] = pd.DatetimeIndex(df_finance2['orderDate']).month
df_finance2.drop(columns=["comments","requiredDate", "shippedDate"], inplace=True)
blankIndex=[''] * len(df_finance2)
df_finance2.index=blankIndex
df_finance2

fig4, ax4 = plt.subplots()
sn.countplot(data= df_finance2, x="month", hue= "year", ax=ax4, order=df_finance2['month'].unique())
plt.title("Number of Orders not payed per Month", size = 12)
plt.ylabel("Frequency")
plt.xlabel("Month")
plt.legend(loc = "upper center", frameon = True, title= "Year")
plt.rcParams["figure.figsize"] = (10,5.5)
st.pyplot(fig4)




"""## Sales
    The number of products sold by category and by month,
    with comparison and rate of change compared to the same month of the previous year.
"""

query_sales = \
'SELECT \
    MONTH(o.orderDate) as month, \
	YEAR(o.orderDate) as year, \
    productLine, \
    SUM(ot.quantityOrdered) as rate \
FROM products AS p \
JOIN orderdetails AS ot ON ot.productCode = p.productCode \
JOIN orders AS o ON ot.orderNumber = o.orderNumber \
GROUP BY YEAR(o.orderDate), MONTH(o.orderDate), productLine \
ORDER BY productLine, MONTH(o.orderDate);'

# sql to pandas
df_sales = pd.read_sql_query(query_sales, con = connection)
# Version table 1
df_display_sales = df_sales.pivot_table(index=["productLine", "month"], columns=['year'], fill_value=0).copy()
df_display_sales.reset_index(inplace=True)
# Using BlankIndex to print DataFrame without index
blankIndex=[''] * len(df_display_sales)
df_display_sales.index=blankIndex
df_display_sales
# Version table 2
# df_display_sales = df_sales.pivot_table(index=["month"], columns=["productLine", 'year'], fill_value=0).copy()
# df_display_sales.reset_index(inplace=True)
# df_display_sales

# Create bar plot for each product line

idx = pd.date_range(start='2020-01', freq='M', periods=12)
m = idx.to_series().dt.month.values
m_names = idx.to_series().dt.month_name()
for productLine in df_sales.sort_values("rate", ascending=False)["productLine"].unique():
    if df_sales[df_sales['productLine'] == productLine]["productLine"].count() > 4:
      fig, ax = plt.subplots()
      sn.barplot(ax = ax, x='month', y='rate', hue="year", data=df_sales[df_sales['productLine'] == productLine], order=m)
      ax.set_ylim(ymax=df_sales["rate"].max() + 500, ymin=df_sales["rate"].min() )
      plt.legend(loc = "upper left", frameon = True, title= "Year")
      ax.set(title = f"{productLine}'s rate per Month and Year")
      st.pyplot(fig)


"""## Human Resources
    Each month, the 2 sellers with the highest turnover.
"""

query_hr = \
'WITH t1 AS (SELECT \
	  YEAR(payments.paymentDate) as year, \
    MONTH(payments.paymentDate) as month, \
    customers.salesRepEmployeeNumber as seller_id, \
    firstName as seller_first_name, \
    lastName as seller_last_name, \
    SUM(payments.amount) as amount, \
    ROW_NUMBER() OVER(PARTITION BY year, month ORDER BY amount DESC) AS position \
FROM payments \
  LEFT JOIN customers \
    ON payments.customerNumber = customers.customerNumber \
  LEFT JOIN employees \
    ON employeeNumber = salesRepEmployeeNumber \
  GROUP BY employeeNumber, MONTH(paymentDate), YEAR(paymentDate) \
  ORDER BY year, month, amount DESC) \
SELECT * FROM t1 \
  WHERE position < 3 \
  ORDER BY year DESC, month DESC, position;'

# sql to pandas
df_hr = pd.read_sql_query(query_hr, con = connection)
# change the month number to name month
st.write("Position and turnover by month")
df_hr_display = df_hr.set_index(['year', 'month', "position"]).copy()
#df_hr_display.index.set_names({'year', 'month', "position"}, inplace=True)
st.write(df_hr_display.to_html(), unsafe_allow_html=True)
