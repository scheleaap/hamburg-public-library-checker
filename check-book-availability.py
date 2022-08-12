#!/usr/bin/env python3

import argparse
import logging
import requests

def parse_arguments_and_environment(raw_args, environ):
    parser = argparse.ArgumentParser(
        description="Activates a model.",
        epilog=ARGPARSE_REPOSITORY_CREDENTIALS_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    # This requires 'model' to be an optional argument otherwise the usage help text would be misleading
    # https://stackoverflow.com/questions/5854920/
    parser.add_argument('-m', "--model", required=True,
                        help="The id of the model you want to deploy to a customer.")
    parser.add_argument('-l', "--channel", required=True, help="The channel you want to deploy the model to.")
    parser.add_argument("-c", '--customer', required=True, help="The customer you want to deploy to.")
    parser.add_argument("-e", '--environment', nargs='+',
                        help="The environment(s) you want to deploy to. "
                             "Required if --create is provided. "
                             "If you do not specify an environment you will deploy to all configured environments "
                             "(normally integration, staging and prod)!")
    parser.add_argument("--create", action='store_true',
                        help="Create a new environment file(s) for the customer. "
                             "The script will fail if --create is specified and one or more files already exist, "
                             "or if --create is _not_ specified and one or more files do _not_ exist.")
    parser.add_argument("--yolo", action="store_true",
                        help=argparse.SUPPRESS)  # Directly commit to master instead of creating a PR.

    args = parser.parse_args(raw_args)
    if args.create and not args.environment:
        parser.error("the --environment argument is required if --create is specified")
    env_vars = get_credentials_or_exit(environ, raw_args, parser)

    return args, env_vars


def main(args, env_vars):
    new_model_id = args.model
    new_channel_id = transform_channel_name(args.channel)
    repository_user = env_vars.REPOSITORY_USER
    repository_password = env_vars.REPOSITORY_PASS

    verify_model_exists_or_exit(new_model_id, repository_user, repository_password)

    with ModelActivations() as ma:
        environments = verify_and_select_environments_or_exit(args, ma)

        if not args.yolo:
            logging.debug("Creating new branch...")
            branch_prefix = f"new-model-{new_model_id}"
            branch_name = ma.create_new_branch(branch_prefix)
        else:
            branch_name = "master"

        logging.debug(f"Modifying environment files on branch {branch_name}...")
        ma.modify(
            customers=[args.customer],
            environments=environments,
            modification_function=set_model(new_channel_id, new_model_id)
        )

        commit_msg = f"Update model to {new_model_id} for customer {args.customer} and environments {args.environment}"
        commit_created = ma.commit_all(commit_msg)

        if commit_created:
            ma.push_branch(branch_name)
            logging.debug(f"Pushed to branch {branch_name}.")

            if not args.yolo:
                create_pr_in_browser(branch_name)
        else:
            logging.info("No changes.")


if __name__ == "__main__":
    setup_logging()
    main(*parse_arguments_and_environment(sys.argv[1:], os.environ))
