# Hamburg Public Library Checker

The HHPL Checker notifies you through [IFTTT](https://ifttt.com/) when a book is available at [Hamburg's public library](https://www.buecherhallen.de/).

## Usage

First, set up an IFTTT [webhook](https://ifttt.com/maker_webhooks) named `hhpl` and copy the key.

```sh
$ ./notify_book_availability.sh --ifttt_key=<key> T021736375
```

## Technical Details

The tool uses the public [SOAP and JSON web service](https://zones.buecherhallen.de/app_webuser/WebUserSvc.asmx). I only discovered the existence of this API through [paper](https://github.com/q231950/paper), a tool to manage your library account.
