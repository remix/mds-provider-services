FROM CityofSantaMonica/mds-provider-services

COPY . .

RUN pipenv install

# sets up an "executable container" for the data load script
ENTRYPOINT ["python", "main.py"]