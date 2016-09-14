# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import os
import os.path
import shutil
import tempfile
import zipfile
from contextlib import closing

import boto3
from future.moves.urllib.request import urlopen
from general_tools.file_utils import unzip

from convert import convert

here = os.path.abspath(os.path.dirname(__file__))
DEFAULT_CSS = os.path.join(here, "default.css")


def handle(event, context):
    job = retrieve(event, "job", "payload")
    # source: URL of zip archive of input USFM files
    source = retrieve(job, "source", "\"job\"")
    # stylesheets: (optional) list of CSS filenames
    stylesheets = [os.path.basename(DEFAULT_CSS)]
    if "stylesheets" in job:
        stylesheets.extend(job["stylesheets"])
    upload = retrieve(event, "upload", "payload")
    cdn_bucket = retrieve(upload, "cdn_bucket", "\"upload\"")
    cdn_file = retrieve(upload, "cdn_file", "\"upload\"")

    print('source: {}'.format(source))
    print('stylesheets: {}'.format(stylesheets))
    print('cdn_bucket: {}'.format(cdn_bucket))
    print('cdn_file: {}'.format(cdn_file))

    download_dir = tempfile.mkdtemp("download")
    scratch_dir = tempfile.mkdtemp("extracted")

    # download  and unzip the archive (source)
    basename = os.path.basename(source)
    downloaded_file = os.path.join(download_dir, basename)
    download_file(source, downloaded_file)
    unzip(downloaded_file, scratch_dir)

    inputs = [filename for (root, dirs, filenames) in os.walk(scratch_dir)
              for filename in filenames]
    outputs = convert(inputs, output_dir=scratch_dir, stylesheets=stylesheets)

    zip_file = os.path.join(scratch_dir, 'result.zip')
    with zipfile.ZipFile(zip_file, "w") as zf:
        zf.write(DEFAULT_CSS, os.path.basename(DEFAULT_CSS))
        for filename in outputs:
            zf.write(filename, os.path.basename(filename))

    print("Uploading {0} to {1}/{2}".format(zip_file, cdn_bucket, cdn_file))
    boto3.client('s3').upload_file(zip_file, cdn_bucket, cdn_file)

    return {
        'success': True,
    }


def download_file(url, outfile):
    """
    Downloads a file from url and saves it to outfile.
    """
    print("Downloading {}".format(url))
    with closing(urlopen(url)) as request:
        with open(outfile, 'wb') as fp:
            shutil.copyfileobj(request, fp)


def retrieve(dictionary, key, dict_name=None):
    """
    Retrieves a value from a dictionary, raising an error message if the
    specified key is not valid
    :param dict dictionary:
    :param key:
    :param str|unicode dict_name: name of dictionary, for error message
    :return: value corresponding to key
    """
    if key in dictionary:
        return dictionary[key]
    dict_name = "dictionary" if dict_name is None else dict_name
    raise Exception("{k} not found in {d}".format(k=repr(key), d=dict_name))
