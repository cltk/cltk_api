[![Join the chat at https://gitter.im/cltk/cltk_api](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/cltk/cltk_api?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

# Notice

The Classics Archive application is currently under active development and is not ready for production.

# About

A simple Flask app for accessing corpora from the CLTK corpora.  Currently under development.

To run with gunicorn: `gunicorn -w 4 -b 0.0.0.0:5000 api_json:app`.

## Development

To get started developing, you'll need Python3.5 and Mongo installed.

Create a virtual environment and activate it:

`$ pyvenv venv`
`$ source venv/bin/activate`

Install dependencies:

`$ pip install -r requirements.txt`

Finally, start the app with the following command:

`$ python api_json.py`


