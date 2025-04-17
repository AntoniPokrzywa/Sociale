<img  src=".github/assets/sociale-backend.png">
<h3  id="readme-top" align="center">Sociale</h3>
<p align="center">
    Seamless real-time bike rental management
    <br />
    <a href="https://github.com/AntoniPokrzywa/Sociale/tree/main/docs"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://sociale.apokrzywa.tech/bikes/">View Demo</a>
    ·
    <a href="https://github.com/AntoniPokrzywa/Sociale/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/AntoniPokrzywa/Sociale/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
  
  
<!-- GETTING STARTED -->
## Getting Started

Sociale helps you share bikes among friends with ease. It's really easy to set up and provides everything you need to manage bike rentals, including bike locations, parking areas, and rentals.

You can define who is allowed to rent bikes, specify safe spots for locking them, and save extra money by avoiding costly commercial bike or electric scooter rentals

### Prerequisites

Make sure Docker is installed. You can download it from [here](https://www.docker.com/get-started)
```sh
docker --version
```

### Installation

1. **Clone the repository**  
   First, clone the repository:
   ```bash
   git clone https://github.com/antonipokrzywa/sociale
   cd https://github.com/antonipokrzywa/sociale

2. **Set up environment variables**  
   Ensure the `.env` file is present and properly configured with as follows:
    ```python
    POSTGRES_DB=<your_database_name>
    POSTGRES_USER=<your_database_user>
    POSTGRES_PASSWORD=<your_database_password>
    POSTGRES_HOST=<your_database_host>         
    POSTGRES_PORT=5432
    DB_IGNORE_SSL=<true|false>
    ```
    If you are planning to use email verification and password reset make sure to add these variables too:
    ```python
    EMAIL_HOST=<your_smtp_host>                
    EMAIL_PORT=<your_email_port>
    EMAIL_HOST_USER=<your_email_address>
    EMAIL_HOST_PASSWORD=<your_email_password>
    EMAIL_USE_TLS=<true|false> 
    ```
   You can also add `DJANGO_SUPERUSER_EMAIL` and `DJANGO_SUPERUSER_PASSWORD` for automatic superuser creation

> [!IMPORTANT]  
> Don't forget about creating a secret key and setting the `DJANGO_SECRET_KEY` in your environment variables.  Ensure that it is kept secure and never shared publicly.



1. **Set up the Docker container**  
   Build and start the Docker containers:
   ```bash
   docker compose up --build
   ```

2. **Access the app**  
   Once the containers are up, the app will be available at:
   ```bash
   http://localhost:8000
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Overview

If you are only here  for api docs click <a href="./docs/api_reference.md"> here </a>

This project is composed of four main applications: Users, Bikes, Parkings, and Rentals. Below is a brief description of what each app does:


- **Users**
  - Allows users to create an account, log in, verify their email, and reset passwords securely.
  - Admins can manage all user accounts in the system.
  - Includes status control (active/verified/staff).

- **Bikes**
  - Returns available bikes on  for users that are verified and active
  - Admins can list, add, update, and remove bikes
  - Each bike has location, availability, and QR code data

- **Parkings**
  - Returns parking zones for displaying them on the map.
  - Admins can perform CRUD operations on them

- **Rentals**
  - Users can start and finish a bike rental (must be verified + activated).
  - Admins can monitor all rentals, filter by status/user and update them if neccessary

Additionally, any unauthorized access attempts are logged and can be reviewed by admins


<p align="right">(<a href="#readme-top">back to top</a>)</p>


## License

Distributed under the MIT License. See `LICENSE.txt` for more information.



<!-- CONTACT -->
## Contact

Antoni Pokrzywa - [/in/antonipokrzywa/](https://www.linkedin.com/in/antonipokrzywa/) - antonipokrzywa@gmail.com

Project Link: [https://github.com/AntoniPokrzywa/Sociale](https://github.com/AntoniPokrzywa/Sociale)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
