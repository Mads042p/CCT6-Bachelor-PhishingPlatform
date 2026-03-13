# CCT6-Bachelor-PhishingPlatform

This project is a bacehlor project ...

### Style guide

All functions made to be used outside of the code file should have a docstring
```
def SQLRequestPassword(Username)
    ```This method fetches the password
    connected to the username
    Input: String
    Output: String```

    SQLRequest = "SELECT password FROM users WHERE username = Username 
```


All functions sending or receiving data, website to email scanner etc., should be JSON format

```
{
  "first_name": "John",
  "last_name": "Smith",
  "is_alive": true,
  "age": 27,
  "address": {
    "street_address": "21 2nd Street",
    "city": "New York",
    "state": "NY",
    "postal_code": "10021-3100"
  }
}
```