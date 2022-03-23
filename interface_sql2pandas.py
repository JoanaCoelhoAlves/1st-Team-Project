# -*- coding: utf-8 -*-


# streamlit_app.py
"""interface_sql2pandas.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1FRPmPH4y24A0vxSuqqQa6ZBOR1NU6C9U
"""

#!pip install mysql-connector

# Import libraries
import mysql.connector
import pandas as pd
import streamlit as st
import getpass
import seaborn as sn
from matplotlib import pyplot as plt

links = ["<a href='#logistic'>Logistic</a>",\
         "<a href='#finances-1'>Finances 1</a>",\
         "<a href='#finances-2'>Finances 2</a>",\
         "<a href='#sales'>Sales</a>",\
         "<a href='#human-ressources'>Human ressources</a>"]
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
  "SELECT o.productCode, p.productName, SUM(o.quantityOrdered) as qty_ordered, p.quantityInStock as available_qty FROM orderdetails as o\
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

# Set plot
fig1, ax1 = plt.subplots()
df_logistic.set_index("productName").plot(kind="bar", \
                 title="The stock of the 5 most ordered products.",\
                 xlabel="Product code",\
                 rot=0,\
                 ax = ax1,\
                 ylabel="Quantity").legend(["Ordered", "Available"])
st.pyplot(fig1)

"""## Finances 1
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
df_finance1

#create the bar chart
fig3, ax3 = plt.subplots()
df_finance1.plot.bar(x="country", \
                     y="turnover (€)", \
                     title= "The turnover of the orders in the last two months, by country", \
                     ylabel= "turnover (€)", \
                     legend = False,\
                     figsize= (10, 3),\
                     ax=ax3)
st.pyplot(fig3)

"""## Finances 2
    Orders that have not yet been paid.
"""

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
WHERE NOT orderNumber IN ( \
SELECT o.orderNumber FROM sub_order as o \
JOIN payments as p ON p.customerNumber = o.customerNumber \
WHERE p.amount = o.amount_order) \
AND NOT status = "cancelled";' \

# sql to pandas
df_finance2 = pd.read_sql_query(query_finance_two, con = connection)
df_finance2["Lag"] = df_finance2["shippedDate"] - df_finance2["orderDate"]
maximum_lag= max(df_finance2["Lag"])
minimum_lag = min(df_finance2["Lag"])

print("The maximum lag time is: " + str(maximum_lag) + "\n" + "The minimum lag time is: " + str(minimum_lag) + "\n")

df_finance2['year'] = pd.DatetimeIndex(df_finance2['orderDate']).year
df_finance2['month'] = pd.DatetimeIndex(df_finance2['orderDate']).month


fig4, ax4 = plt.subplots()
sn.countplot(data= df_finance2, x="month", hue= "year", ax=ax4)
plt.title("Number of Orders per Month", size = 12)
plt.ylabel("Frequency")
plt.xlabel("Month")
plt.legend(loc = "upper center", frameon = True, title= "Year")
plt.rcParams["figure.figsize"] = (10,5.5)
st.pyplot(fig4)

#finance2_plot.unstack(level=0).plot(kind="bar", ax=ax4, rot = 0, layout= (3,12), xlabel= "Months", ylabel = "Frequency" , title= "Number of Orders per month" )


"""## Sales
    The number of products sold by category and by month,
    with comparison and rate of change compared to the same month of the previous year.
"""

query_sales = \
'SELECT \
    {fn MONTHNAME(o.orderDate)} as month, \
	YEAR(o.orderDate) as year, \
    productLine, \
    SUM(ot.quantityOrdered) as rate \
FROM products AS p \
JOIN orderdetails AS ot ON ot.productCode = p.productCode \
JOIN orders AS o ON ot.orderNumber = o.orderNumber \
GROUP BY YEAR(o.orderDate), MONTH(o.orderDate) \
ORDER BY productLine, MONTH(o.orderDate);'

# sql to pandas
df_sales = pd.read_sql_query(query_sales, con = connection)
first = df_sales.loc[(df_sales["year"] == 2020) | (df_sales["year"] == 2021),:]
second = df_sales.loc[(df_sales["year"] == 2021) | (df_sales["year"] == 2022),:]
st.header("Sales from 2020 - 2021")
first
st.header("Sales from 2021 - 2022")
second

# Create bar plot for each product line


"""## Human ressources
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
df_hr
