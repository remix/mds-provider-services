FROM CityofSantaMonica/mds-provider-services

COPY . .

RUN pipenv install

# sets up an "executable container" for the api script
ENTRYPOINT ["python", "main.py"]