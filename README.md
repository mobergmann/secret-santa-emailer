# secret-santa-emailer
A python application, which calculates secret santas and informs the user via email


## Look of a json
### Example
```json
{
    "sender": {
        "address": "",
        "email": "",
        "port": 0,
        "subject": "",
        "body": ""
    },
    "santas": [
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

### Documentation
- `sender`: Contains all relevant information for sending the emails
  - `address`: URL to the email upload server
  - `email`: Email address, from which the emails are being send
  - `port`: Port number from which the server sends the emails
  - `subject`: The subject of the email to be sent
  - `body`: The body of the email to be sent
- `users`: A list of all objects, which are the secret santas
  - `name`: The name of the user/ secret santa, which is being gifted
  - `email`: Email address of the user/ secret santa, which is being gifted

## Addressing a Secret Santa
You can insert the name or email of the Secret Santa as well as the name or email of the recipiant into the emails subject or body/ message.
This can be done by using special reserved text codes:

 - `{santa.name}`
 - `{santa.email}`
 - `{recipient.name}`
 - `{recipient.email}`

The subject and the body will be scanned for occurrences of this kind of formatting and be replaced with the according value.
As there is no way to escape this functionality, be sure not to write these code snipped accidentally. 

### Example
```
"subject": "Hello {santa.name}, you need to gift {recipient.name}!"
```

## Newlines in email body
To insert newlines into the body of the email just write an `\n` instead of the multiline.
The whole body in the json must be a single line.


## Running the Program
To run the program add an appropriate json file (see #Look of a json).
You need to have python3 installed.  
Then you can launch the program with `python3 main.py <path to json>`
