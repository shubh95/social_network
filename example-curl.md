# signup
curl -X POST http://0.0.0.0:8000/register/ \
-H "Content-Type: application/json" \
-d '{
    "email": "shubhvas95@gmail.com",
    "password": "admin1234",
    "first_name": "shubham",
    "last_name": "vashisht"
}'

curl -X POST http://0.0.0.0:8000/register/ \
-H "Content-Type: application/json" \
-d '{
    "email": "salvationmoksh1996@gmail.com",
    "password": "admin1234",
    "first_name": "moksh",
    "last_name": "vashisht"
}'

curl -X POST http://0.0.0.0:8000/register/ \
-H "Content-Type: application/json" \
-d '{
    "email": "akshitverma@gmail.com",
    "password": "admin1234",
    "first_name": "Akshit",
    "last_name": "Verma"
}'

# login as shubham
curl -X POST http://0.0.0.0:8000/login/ \
-H "Content-Type: application/json" \
-d '{
    "email": "shubhvas95@gmail.com",
    "password": "admin1234"
}'

# search 'ksh'
curl -X GET http://0.0.0.0:8000/search/?q=ksh \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI3ODA4MjY1LCJpYXQiOjE3Mjc4MDc5NjUsImp0aSI6IjIwMzViODlhOTIwZjQ0N2FhNDBiODNlMDE5YjNhNmU0IiwidXNlcl9pZCI6MX0.4W83g2OP2Dm68T2BvfLLCo6jsFP7QTRTDvHqIyBp0H0" \
-H "Content-Type: application/json"