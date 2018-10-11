import argparse
import boto3
from configparser import ConfigParser
from datetime import datetime, timedelta
import dateutil.parser
import json
import mds
from mds.api.client import ProviderClient
import mds.providers
import os
import time
from uuid import UUID


def setup_cli():
    """
    Create the cli argument interface, and parses incoming args.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--aws_region",
        type=str,
        help="The AWS region to use for S3 uploads. Only applies when given with\
        the --s3_bucket argument. Overrides the AWS_DEFAULT_REGION environment variable.\
        If AWS_DEFAULT_REGION is not set, this parameter must be given."
    )
    parser.add_argument(
        "--bbox",
        type=str,
        help="The bounding-box with which to restrict the results of this request.\
        The order is southwest longitude, southwest latitude, northeast longitude, northeast latitude.\
        For example: --bbox -122.4183,37.7758,-122.4120,37.7858"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to a provider configuration file to use.\
        The default is `.config`."
    )
    parser.add_argument(
        "--device_id",
        type=str,
        help="The device_id to obtain results for.\
        Only applies to --trips."
    )
    parser.add_argument(
        "--duration",
        type=int,
        help="Number of seconds; with --start_time or --end_time,\
        defines a time query range."
    )
    parser.add_argument(
        "--end_time",
        type=str,
        help="The end of the time query range for this request.\
        Should be either int Unix seconds or ISO-8061 datetime format.\
        At least one of end_time or start_time is required."
    )
    parser.add_argument(
        "--no_paging",
        action="store_true",
        help="Flag indicating paging through the response should *not* occur.\
        Return *only* the first page of data."
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Base path to write data files into."
    )
    parser.add_argument(
        "--providers",
        type=str,
        nargs="+",
        help="One or more providers to query, separated by commas.\
        Could be provider_name or provider_id.\
        The default is to query all configured providers."
    )
    parser.add_argument(
        "--ref",
        type=str,
        help="Git branch name, commit hash, or tag at which to reference MDS.\
        The default is `master`."
    )
    parser.add_argument(
        "--s3_bucket",
        type=str,
        help="AWS S3 bucket to store data files in. When used with --output,\
        a common key prefix is given to data files. AWS credentials must be configured;\
        use AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env vars or standard AWS\
        credential configuration in e.g. ~/.aws/credentials."
    )
    parser.add_argument(
        "--start_time",
        type=str,
        help="The beginning of the time query range for this request.\
        Should be either int Unix seconds or ISO-8061 datetime format.\
        At least one of end_time or start_time is required."
    )
    parser.add_argument(
        "--status_changes",
        action="store_true",
        help="Flag indicating Status Changes should be requested."
    )
    parser.add_argument(
        "--trips",
        action="store_true",
        help="Flag indicating Trips should be requested."
    )
    parser.add_argument(
        "--vehicle_id",
        type=str,
        help="The vehicle_id to obtain results for.\
        Only applies to --trips."
    )

    return parser, parser.parse_args()

def parse_time_range(args):
    """
    Returns a valid range tuple (start_time, end_time) given an object with some mix of:
         - start_time
         - end_time
         - duration

    If both start_time and end_time are present, use those. Otherwise, compute from duration.
    """
    def _to_datetime(input):
        """
        Helper to parse different textual representations into datetime
        """
        return dateutil.parser.parse(input)

    if args.start_time is not None and args.end_time is not None:
        return _to_datetime(args.start_time), _to_datetime(args.end_time)

    duration = int(args.duration)

    if args.start_time is not None:
        start_time = _to_datetime(args.start_time)
        return start_time, start_time + timedelta(seconds=duration)

    if args.end_time is not None:
        end_time = _to_datetime(args.end_time)
        return end_time - timedelta(seconds=duration), end_time

def parse_config(path):
    path = path or os.path.join(os.getcwd(), ".config")
    print("Reading config file:", path)

    config = ConfigParser()
    config.read(path)

    return config

def provider_names(providers):
    """
    Returns the names of the :providers:, separated by commas.
    """
    return ", ".join([p.provider_name for p in providers])

def runtime_providers(registry, args):
    """
    Returns the portion of :registry: requested by the given runtime :args:.
    """
    if args.providers is None:
        return registry
    else:
        names, ids = [], []
        for p in args.providers:
            try:
                id = UUID(p)
                ids.append(id)
            except:
                names.append(p.lower())

        return [p for p in registry \
                if p.provider_name.lower() in names or p.provider_id in ids]

def file_name(output, datatype, provider, start_time, end_time):
    """
    Generate a filename from the given parameters.
    """
    fname = f"{datatype}_{provider}_{start_time.isoformat()}_{end_time.isoformat()}.json"
    return os.path.join(output, fname) if output else fname

def dump_payloads(payloads, output, datatype, start_time, end_time, **kwargs):
    """
    Write a the :payloads: mapping (provider name => data payload) to json files in :output:.

    Optionally provide :kwargs: for s3_service and s3_bucket information.
    """
    if "s3_bucket" in kwargs:
        s3bucket = kwargs["s3_bucket"]
        s3 = getattr(kwargs, "s3_service", s3_service())
        print("In S3 bucket: {}".format(s3bucket))
    else:
        print("In {}".format(output))

    for provider, payload in payloads.items():
        fname = file_name(output, datatype, provider.provider_name, start_time, end_time)
        if "s3_bucket" in kwargs:
            body = json.dumps(payload).encode()
            s3.Object(bucket_name=s3bucket, key=fname).put(Body=body)
        else:
            with open(fname, "w") as f:
                json.dump(payload, f)

def s3_service(region_name=None):
    """
    Helper to return an s3 service using :region_name: or environment variables.
    """
    if region_name:
        return boto3.resource("s3", region_name=region_name)

    return boto3.resource("s3")

if __name__ == "__main__":
    arg_parser, args = setup_cli()

    # assert the time range parameters and parse a valid range
    if args.start_time is None and args.end_time is None:
        arg_parser.print_help()
        exit(1)

    if (args.start_time is None or args.end_time is None) and args.duration is None:
        arg_parser.print_help()
        exit(1)

    start_time, end_time = parse_time_range(args)

    # parse the config file
    config = parse_config(args.config)

    # determine the MDS version to reference
    ref = args.ref or config["DEFAULT"]["ref"] or "master"
    print(f"Referencing MDS @ {ref}")

    # used in later requests
    kwargs = {}

    # determine output destination
    if args.s3_bucket is not None:
        try:
            s3 = s3_service(region_name=args.region_name)
            kwargs["s3_bucket"] = args.s3_bucket
            kwargs["s3_service"] = s3
        except Exception as ex:
            print("You must configure AWS credentials to use S3.")
            print("Set the environment variables: AWS_AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.")
            print("Or configure credentials in the default location (usually ~/.aws/credentials.")
            print("AWS_DEFAULT_REGION environment variable or --aws_region parameter are also required.")
            print(ex)
            exit(1)
    elif args.output is not None:
        os.makedirs(args.output, exist_ok=True)

    # download the Provider registry and filter based on params
    print("Downloading provider registry...")
    registry = mds.providers.get_registry(ref)

    print(f"Acquired registry: {provider_names(registry)}")

    # filter the registry with cli args, and configure the providers that will be used
    providers = [p.configure(config, use_id=True) for p in runtime_providers(registry, args)]
    print(f"Requesting from providers: {provider_names(providers)}")

    # initialize an API client for these providers and configuration
    client = ProviderClient(providers)

    print(f"Time range: {start_time.isoformat()} to {end_time.isoformat()}")

    # download Status Changes
    if args.status_changes:
        print("Requesting Status Changes")

        status_changes = client.get_status_changes(providers=providers,
                                                   start_time=start_time,
                                                   end_time=end_time,
                                                   bbox=args.bbox,
                                                   page=not args.no_paging)

        print(f"Writing Status Changes data file(s)")

        dump_payloads(payloads=status_changes,
                      output=args.output,
                      datatype=mds.STATUS_CHANGES,
                      start_time=start_time,
                      end_time=end_time,
                      **kwargs)

        print(f"Status Changes download complete")

    # download Trips
    if args.trips:
        print("Requesting Trips")

        trips = client.get_trips(providers=providers,
                                 device_id=args.device_id,
                                 vehicle_id=args.vehicle_id,
                                 start_time=start_time,
                                 end_time=end_time,
                                 bbox=args.bbox,
                                 page=not args.no_paging)

        print(f"Writing Trips data file(s)")

        dump_payloads(payloads=trips,
                      output=args.output,
                      datatype=mds.TRIPS,
                      start_time=start_time,
                      end_time=end_time,
                      **kwargs)

        print(f"Trips download complete")

