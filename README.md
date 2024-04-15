----How to run------------------------

1)Clone the repo

2)Make a virtual environment

3)pip install requirements.txt -  to install dependencies

4)cd projectname - in order to come to main directory

5)Type these two commands: i) python manage.py makemigrations myapp    ii) python manage.py migrate

6)python manage.py runserver - to run this server  

--Output-Screenshot of the APIs------------------------

-Create User

i) success ![Create-User-Success](https://github.com/sarthak37/Brightmoney-task/assets/52873771/ac5fa7ea-31ff-42db-9f6d-9dcea80d4f7d)

ii) error  ![Error](https://github.com/sarthak37/Brightmoney-task/assets/52873771/c78be3a0-53f5-4a4b-84bc-3c11cd7506e7)
iii) sql-collection users ![sql-collection-User](https://github.com/sarthak37/Brightmoney-task/assets/52873771/f111d91b-9a1d-481b-a69a-f3d5062a1bff)

-Apply Loan

i)success ![Apply-Loan-Success](https://github.com/sarthak37/Brightmoney-task/assets/52873771/abe00b92-34cb-4480-9fa3-7f8bc70c3918)
ii)error ![Error-applyloan](https://github.com/sarthak37/Brightmoney-task/assets/52873771/2cdb8b33-d1fe-4f3e-92a1-79a5f76de6d5)
iii)sql-collection-loans ![sql-collection-applyloan](https://github.com/sarthak37/Brightmoney-task/assets/52873771/58819cac-c419-4e63-8f73-08b4260b0905)

-Make-Payement

i)success ![Make-payement-success](https://github.com/sarthak37/Brightmoney-task/assets/52873771/d96c2322-df0f-4852-89ba-5a59cbda51a2)
ii)error ![Error-previous-emi-unpaid](https://github.com/sarthak37/Brightmoney-task/assets/52873771/7eab0054-7f79-4482-a3b1-b553f31c4f1f)
iii)sql-collection-payments ![sql-collection-make-payement](https://github.com/sarthak37/Brightmoney-task/assets/52873771/4e35a451-24bf-4645-98e7-27050d450278)

-Loan-status-dues-paidamount

i)loan status of first loan id ![loan-status-A](https://github.com/sarthak37/Brightmoney-task/assets/52873771/c42a2236-f193-40d0-9df8-9118a0636f27)
ii)loan status of second loan id ![loan-status-B](https://github.com/sarthak37/Brightmoney-task/assets/52873771/12297eb8-2c83-4a76-b9a8-b267e9205690)
iii)loan status of third loan id ![loan-status-C](https://github.com/sarthak37/Brightmoney-task/assets/52873771/fa49119e-1ee5-4b0f-b11a-3f89e436d6f0)

-Cronjob


i)billing remaining for that month ![users-billing-remaining](https://github.com/sarthak37/Brightmoney-task/assets/52873771/8d39eb2e-dba6-44c0-9d30-5b068cd96f39)
ii)sql-collection-payment for finding when users paid their emis  ![sql-collection-emi-paid-user-info](https://github.com/sarthak37/Brightmoney-task/assets/52873771/d5a43990-fb0b-4af6-8f95-da1be31ab257)






