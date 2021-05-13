#### Budgeting App.

A Kivy app for monitoring bills, income, and spending, 
giving totals of monthly spend, and funds remaining.

Contains a user logon system to track the budgets of multiple users.
Data is stored in a MySQL database.
<br><br>
###### Prerequisites:

Create Database and database server. 
Use XAMPP control panel and PHPMyadmin to set up local DB server.
createtables.sql will create required database and table structure.
<br><br>

###### Functionality:

From logon screen can create new user to add to the database or log on as an existing user.

Enter Payment, Enter Bill, Amend Income screens are set up to allow payments,
bills and spending to be added. Each screen will update with a summary of the current month's figures.

The main menu will show summaries of total income, total spend, total bills and total finds remaining.
<br><br>
 
###### Planned features:

Amend bills and review spending buttons are not yet linked to any functionality.
The review spending feature will be a way to summarise reports based on different criteria, eg month/year, categories etc.

The aim is to port to build as an android app, prior to this will have to set up the database on a web server instead of locally.
