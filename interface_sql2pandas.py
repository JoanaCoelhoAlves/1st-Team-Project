# -*- coding: utf-8 -*-
"""interface_sql2pandas.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1FRPmPH4y24A0vxSuqqQa6ZBOR1NU6C9U
"""

!pip install mysql-connector

# Import libraries
import mysql.connector
import pandas as pd

import getpass
import seaborn as sn
from matplotlib import pyplot as plt

# Define connection and query

# # Connection with private password
# p = getpass.getpass("What's the password?")
# connection = mysql.connector.connect(user = 'toyscie', password = p, host = '51.68.18.102', port = '23456', database = 'toys_and_models', use_pure = True)

# Connection with public password
connection = mysql.connector.connect(user = 'toyscie', password = 'WILD4Rdata!', host = '51.68.18.102', port = '23456', database = 'toys_and_models', use_pure = True)

#query = "SELECT * from orders WHERE orderDate like '2022-02%'"

"""## Logistic: The stock of the 5 most ordered products.

"""

# \ to go to the new line if the code is too long
query_logistic = \
  "SELECT o.productCode, SUM(o.quantityOrdered) as qty_ordered, p.quantityInStock as available_qty FROM orderdetails as o\
  JOIN products as p ON p.productCode = o.productCode\
  GROUP BY p.productCode\
  ORDER BY SUM(o.quantityOrdered) DESC\
  LIMIT 5;"

# sql to pandas
df_logistic = pd.read_sql_query(query_logistic, con = connection)
df_logistic

df_logistic.info()

#change the qty_ordered from a float variable to an intenger variable
#change the index column, instead of starting in 0 we want to start at 1
#check correlation among variables

#transform the qty_order from a float to an int
df_logistic['qty_ordered'] = df_logistic['qty_ordered'].astype('int')
df_logistic.info()


#startthe index on 1 instead on 0
df_logistic.index = df_logistic.index +1 
df_logistic.head(5)


#check the correlation 
df_logistic.corr()

#conclusion: there is a positive correlation amon qty_ordered and qty_availability
#and a large effect. This means that if the quantity ordered increases tha available quantity also increases

# Use panda to create plot
# Set index to have the right xtiks
df_logistic.set_index("productCode").plot(kind="bar", \
                 title="The stock of the 5 most ordered products.",\
                 xlabel="Product code",\
                 # SET xtick normal rotation\
                 rot=0,\
                 # Fct legend to set right datas  
                 ylabel="Quantity").legend(["Ordered", "Available"])

"""
## Finances 1
The turnover of the orders of the last two months by country"""

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

# sql to pandas
df_finance1 = pd.read_sql_query(query_finance_one, con = connection)
df_finance1.info()
df_finance1

#insert the currency in variable turnover ($ vs€)
#reset the index, so start at 1 the country with highest turnover....
#create a bar chart
#create a pie chart (need to convert to %)

#insert the currency: we assume it is €
df_finance1.rename(columns = {"turnover": "turnover (€)"}, inplace= True)

#reset the index to start at 1 and not at 0
#df_finance1.index = df_finance1.index +1 

df_finance1.head(7)

#create the bar chart 
df_finance1.plot.bar(x="country", y="turnover (€)", title= "The turnover of the orders in the last two months, by country", ylabel= "turnover (€)", legend = False,figsize= (10, 3))

"""
## Finances 2
Orders that have not yet been paid."""

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

df_finance2.info()

#convert orderDate into a date 
#df_finance2["orderDate"] = pd.to_datetime(df_finance2["orderDate"], yearfirst=True)

#convert shippedDate into a date 
#df_finance2["shippedDate"] = pd.to_datetime(df_finance2["shippedDate"], yearfirst=True)

#check if the variable type changed 
#df_finance2.info()

#NOTE: order 10334 is "ON HOLD" without shipped date (which is fine) however order 
#10165 has exactly the same comment as order 10334 but it was already Shipped conatining a 
#"Shipped Date" so there is dubious information regarding the interpretation of the data set 
#because of that we decided to not assign any value to missing comments since comments 
#are not mandatory 

#create a new variable "Lag" which is the difference between shipped date and order date
df_finance2["Lag"] = df_finance2["shippedDate"] - df_finance2["orderDate"]
df_finance2.head(5)
df_finance2.info()

maximum_lag= max(df_finance2["Lag"])
minimum_lag = min(df_finance2["Lag"])
print("The maximum lag time is: " + str(maximum_lag) + "\n" + "The minimum lag time is: " + str(minimum_lag) + "\n")

#convert order date and shipped date to a date type donne 
#state that order 10334 is "ON HOLD" without shipped date (which is fine) however order 10165 has exactly the same comment  donne 
#but it's "Shipped" with a "Shipped Date" so there is an error on the original dataset which is comething to be discussed with the firm

#add a new column with the time difference between shipped date and order date to see the lag donne 
#go to SQL and add a new column with the order amount(in money) it is on due and order customers (customer number) by DESC order to see which 
#clients are more "dangerous" NEED TO BE DONNED 

#create a new variable based on OrderDate that displays the month and organize to see if there is a "bad" month and check the frequency for each month 
#and do a line chart (x-axis is the months and the y-axis is the frequency of the new variable based on the OrderDate)
#present the missing values on variable "comments" and variable "shippedDate" and state that we saw the missing values but decided not to do nothing (and explain why)



#create a new variable based on OrderDate that displays the month and organize to see if there is a "bad" month and check the frequency for each month 
df_finance2['year'] = pd.DatetimeIndex(df_finance2['orderDate']).year
df_finance2['month'] = pd.DatetimeIndex(df_finance2['orderDate']).month


#create the bar plot where on the x-axis are the months and the y-axis the frequency of the orders
finance2_plot= df_finance2.loc[:, ["orderDate", "month", "year"]]
finance2_plot=finance2_plot.groupby(["year", "month"]).count()
finance2_plot.head(20)

finance2_plot.unstack(level=0).plot(kind="bar",  rot = 0, layout= (3,12), xlabel= "Months", ylabel = "Frequency" , title= "Number of Orders per month" )
plt.show()


"""
## Sales
The number of products sold by category and by month,
with comparison and rate of change compared to the same month of the previous year."""

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
df_sales.head(10)

#need to split the table into 2: the first one only contains values from the year 2020 and 2021
#the second table only contains values from the tear 2021 and 2022 and then calculate the rate difference
#make a line plot for each product line and differentiate different products with a different color and make 
#a second differentiation in terms of dash(something else) lines
#y-axis rate and x-axis with the months
#check the product line with the highest and lowest rate

#split the original dataset with only values from 2020 and 2021
first = df_sales.loc[(df_sales["year"] == 2020) | (df_sales["year"] == 2021),:]
first


#split the original dataset with only values from 2021 and 2022
second = df_sales.loc[(df_sales["year"] == 2021) | (df_sales["year"] == 2022),:]
second

"""
## Human ressources
Each month, the 2 sellers with the highest turnover."""

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

#make a frequency table that show the seller_id and the amount of times 
#he/she hows up in the top seller table 
#calculate the total amount of sales per seller_id and organize it (possible tool for future rewards)
#make a bar plot where we have a bar for each year and make the differentuation based on the bar color
#the x-axis would represent the mounts and the y-axis the sum of the 2 top sellers (amount variable)
#so for each month we have 3 bars with different colors

# sql to pandas
df_hr = pd.read_sql_query(query_hr, con = connection)
df_hr.head()

# Group with amout
gp_with_amount = df_hr.groupby(['year', 'seller_id', 'seller_first_name', 'seller_last_name'], as_index=False)["amount"].sum()\
.sort_values('seller_id')
# Get count per position 
gp_postion_one = df_hr[df_hr['position'] == 1].groupby(["seller_id", "year"], as_index=False)['position'].count()
# # set columns name
gp_postion_one.columns = ['seller_id', 'year', 'N 1st pos']  
gp_postion_two = df_hr[df_hr['position'] == 2].groupby(["seller_id", "year"], as_index=False)['position'].count()
# # set columns name
gp_postion_two.columns = ['seller_id', 'year', 'N 2nd pos']
# # Combine tables
gp_with_amount = pd.merge(gp_with_amount, gp_postion_one, how = "left")
gp_with_amount = pd.merge(gp_with_amount, gp_postion_two, how = "left")
# Correction after merge's errors of 
gp_with_amount.fillna(0, inplace=True)
gp_with_amount['N 2nd pos'] = gp_with_amount['N 2nd pos'].astype("int32")
gp_with_amount['N 1st pos'] = gp_with_amount['N 1st pos'].astype("int32")
gp_with_amount = gp_with_amount.round(2)
gp_with_amount.head(50)

gp_perf_year = df_hr.groupby(['year','month'], as_index=False)["amount"].sum()
for y in gp_perf_year['year'].unique():
  pl = gp_perf_year[gp_perf_year['year'] == y]
  plt.plot(pl['month'], pl['amount'], label=str(y) )
plt.xticks(df_hr['month'].unique())
plt.ylabel("Amount")
plt.xlabel("Month")
plt.title("Performence of sellers during a year")
plt.legend()
plt.show()
