# WiFi Soil Moisture Monitoring System Backend

## Create a user

`curl -X POST -H "Content-Type: application/json" -d '{"username" : "example_user", "password" : "example_pass"}' http://HOST/register`

Returns `{"success":true, "token" : USER_TOKEN, "id" : USER_ID}` on successful user creation

## Login to a user account

`curl -X POST -H "Content-Type: application/json" -d '{"username" : "example_user", "password" : "example_pass"}' http://HOST/users/login`

Returns `{"success":true, "token" : USER_TOKEN, "id" : USER_ID}` on successful user creation 

## Register a sensor

`curl -X POST -H "Content-Type: application/json" -d '{"token" : USER_TOKEN}' http://HOST/users/<user_id>/sensors/create`

Returns `{"success": true, "token": SENSOR_TOKEN, "id" : SENSOR_ID}` on successful sensor creation

## Update current sensor value

`curl -X POST -H "Content-Type: application/json" -d '{"token" : SENSOR_TOKEN, "value" : SENSOR_VALUE}' http://HOST/sensors/<sensor_id>/update`

Returns `{"success":true}` on successful update
