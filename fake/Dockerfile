FROM CityofSantaMonica/mds-provider-services

COPY Pipfile Pipfile

# sets up an "executable container" for the data generation script
ENTRYPOINT ["python", "main.py"]