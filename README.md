# Monero Microservice
Interacting with a wallet-rpc instance to perform actions **on a single wallet**.
Change configuration parameters in *config.ini*.

## Methods

### [GET] get_balance
Shows the wallet balance

### [GET] get_payments/<subaddress>
Lists payments sent to a specific subaddress

### [POST] create_subaddress
Creates a new subaddress to send payments to

### [POST] transfer
Sends funds. Requires to send a *to* param with the destination wallet
and the *amount* in XMR

## TBD
Validation of inputs
Tests