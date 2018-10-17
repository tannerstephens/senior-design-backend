# WiFi Soil Moisture Monitoring System Backend

## Create a user

`curl -X POST -H "Content-Type: application/json" -d '{"username" : "example_user", "password" : "example_pass"}' http://HOST/users/register`

Returns `{"success":true}` on successful user creation 

## Register a sensor

`curl -X POST -H "Content-Type: application/json" -d '{"username" : "example_user", "password" : "example_pass"}' http://HOST/sensors/register`

Returns `{"success": true, "token": SENSOR_TOKEN, "id" : SENSOR_ID}` on successful sensor creation

## Update current sensor value

`curl -X POST -H "Content-Type: application/json" -d '{"token" : SENSOR_TOKEN, "id" : SENSOR_ID, "value" : SENSOR_VALUE}' http://HOST/sensors/update`

Returns `{"success":true}` on successful update
