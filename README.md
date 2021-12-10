# secret-santa-emailer
A python application, which calculates secret santas and informs the user via email


## Example Contacts json
```json
{
    "sender": {
        "address": "",
        "email": "",
        "port": 0
    },
    "users": [
        {
            "name": "",
            "email": ""
        },
        {
            "name": "",
            "email": ""
        },
        {
            "name": "",
            "email": ""
        }
    ]
}
```

- `sender`: Contains all relevant information for sending the emails
  - `address`: URL to the email upload server
  - `email`: Email address, from which the emails are being send
  - `port`: Port number from which the server sends the emails
- `users`: A list of all objects, which are the secret santas
  - `name`: The name of the user/ secret santa, which is being gifted
  - `email`: Email address of the user/ secret santa, which is being gifted
