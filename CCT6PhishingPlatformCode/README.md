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


Readeble code over effecient code. Eg. for loops should rather be 3-5 lines instead of 1 line to inprove readability.


Comment where necessary. Code that does not immedialy explain itself should be commented. This is very much a subjective opinion but try.


Variables names - camelCase
    Longer explainable variable names rather than short ones. Eg. "PassWord" instead of "passwrd"
Functions names - camelCase
Class names - PascalCase
Constants names - ALL_CAPS_WITH_UNDERSCORES