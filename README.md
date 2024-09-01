# RealEstateAPI
API created in FastAPI and SQLAlchemy for managing properties, tenants and leases


## Tech stack
* Python 3.9
* FastAPI
* SQLAlchemy
* MySQL
* Docker with Docker Compose
* Stripe


## Functionalities
* Users can be registered by basic registation or registration with activation via email activation link
* There are 3 user tiers: basic user, staff and superuser 
* Every user can have properties as an owner and can be a tenant and rent properties.
* Users can belong to different companies.
* User and owner can prepare a lease when tenant is going to rent the property with specified conditions and billing periods.
* User can pay the bill with usage of Stripe. The payment link is being send to the tenant's email address.


## Project setup
### IMPORTANT:
In order to execute commands with 'make' in Windows you need to install Chocolatey Package Manager
https://chocolatey.org/

1. Clone repository:
`$ git clone https://github.com/mmyszak999/RealEstateAPI/`
2. In the main directory create '.env' file
3. In '.env' set the values of environment variables (you can copy the content from '.env.template' file, but you still need to get real data from your mailing service and stripe account)
4. To build the project, in the root directory type:
`$ make build`
5. In order to run project type: 
`$ make up`
6. To run migrations type:
`$ make migrations`
7. To create the superuser account type:
`$ make superuser`

After that you can use the project.

## Other information about the project usage:
* JWT authentication is implemented so before making requests, you need to login (GET - api/users/login) with the credentials (email + password) and get the access_token which will be used in the header of the next requests
* Project enables to send emails while activating account or while payment activities (payment request, payment confirmation), but this option is turned off in the .env file (SEND_EMAILS=False)
* Payments requests are generated automatically (via the scheduled job in the src/core/tasks.py) when the lease payment date comes.
* The payment object contains checkout url which enable to pay the rent in the certain billing period
* In the Stripe checkout type test card number:
4242 4242 4242 4242, rest of the data does not matter
* Use the swagger (localhost:8000/docs) in order to check the json shape, schema fields and endpoint names
* In order to pay rent when SEND_EMAILS=False, you need to go to the detail payment view (api/payments/{payment_id}), copy the link in the 'payment_checkout_url' field and open it (you will see stripe checkout site). After successful transaction you can check the payment details another time and you should see the payment_accepted=True
* API offers extra features such as:
    - filtering - example: /api/users/?first_name__ge=chris&birth_date__lt=2000-01-01&is_active__eq=True
    - sorting - example: /api/users/?sort=last_name__asc,birth_date__desc
    - pagination - example: /api/users/?page=2&size=10







## Tests
`$ make test`

## Tests with location 
`$ make test location=tests/test_leases/test_routers.py`

