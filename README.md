<div id="top"></div> 
<!-- Website LOGO -->
<br />
<div align="center">
  <a href="https://aasood.com">
    <img src="https://aasood.com/media/logo/stores/1/file.png" alt="Logo" width="107" height="47">
  </a>
  
<h3 align="center">Basket Microservice</h3>
  
  <p align="center">
    A microservice to handle products baskets!
    <br />
    <a href="#"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="#">View Demo</a>
    ·
    <a href="https://gitlab.aasood.com/ecommerce/backend/basket/-/issues">Report Bug</a>
    ·
    <a href="https://gitlab.aasood.com/ecommerce/backend/basket/-/issues">Request Feature</a>
  </p>
</div>
 
 
<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Road map</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->



### Built With

This section should list any major frameworks/libraries used to bootstrap your project. Leave any add-ons/plugins for
the acknowledgements section. Here are a few examples.

* [Python](https://www.python.org)
* [Fast API](https://fastapi.tiangolo.com)
* [RabbitMQ](https://www.rabbitmq.com)
* Later, [Vue.js](https://vuejs.org) may included.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- GETTING STARTED -->

## Getting Started

In this part, there is an instructions on setting up the project locally. To get a local copy up and running follow
these simple steps.

### Installation

After installing prerequisites, now you can install dependencies of this project:

1. Clone the repo
   ```sh
   git clone http://200.100.100.162/ecommerce/backend/basket.git
   ```
2. Setup an environment
    ```sh
    sudo apt install python3-virtualenv
    virtualenv venv
    source venv/bin/activate
    ```
3. Install pip packages
   ```sh
   pip install -r requirements.txt
   ```
4. In main directory(where `setup.py` file is) use this command to install the project
   ```sh
   pip install -e .
   ```

5. create .env file
   ```text

   # Settings
   
   APP_NAME="Basket-app"
   DEBUG_MODE=1
   
   # RabbitMQ
   
   RABBITMQ_HOST="localhost"
   RABBITMQ_PORT=5672
   RABBITMQ_USER=""
   RABBITMQ_PASSWORD=""
   
   # Uvicorn
   
   UVICORN_HOST="0.0.0.0"
   UVICORN_PORT=8000

   ```

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->

## Usage

To run the project, make sure that the mongodb service is up locally and run this in the app directory

```sh
uvicorn main:app --reload
```

- You can visit [localhost:8000](http://localhost:8000) for root directory.
- The API docs are available at http://localhost:8000/{service-name}/api/v1/docs
- Alternative API docs are also available at http://localhost:8000/{service-name}/redoc

<p align="right">(<a href="#top">back to top</a>)</p>

## Testing

For testing the project, run this command in main directory

```sh
pytest
```

#### Coverage

Testing coverage can also be achieved by:

```shell
pytest --cov
```

<!-- ROADMAP -->

## Roadmap

- [x] CRUD
- [ ] Refactor according to needs

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTRIBUTING -->

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any
contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also
simply open an issue with the tag "enhancement". Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- LICENSE -->

## License

All rights reserved

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTACT -->

## Contact

* Mohamad Ahmadi - mohammadahmadidezhnet@gmail.com

Project
Link: [https://gitlab.aasood.com/ecommerce/backend/basket/](https://gitlab.aasood.com/ecommerce/backend/basket/)

<p align="right">(<a href="#top">back to top</a>)</p>

