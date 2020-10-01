import logging
import argparse
import wget
import xml.dom.minidom
import os
import datetime

parser = argparse.ArgumentParser(description='Download BBB Recording as single files.')

parser.add_argument('hostname', metavar='HOST', type=str, nargs=1,
                    help='the hostname where to download.')
parser.add_argument('recording_id', metavar='REC_ID', type=str, nargs=1,
                    help='the external recording id to download.')
parser.add_argument('--output', nargs='?', help='output folder', dest='output')
parser.add_argument('--log', nargs='?', help='gives informative output during process.', dest='log')

args = parser.parse_args()

hostname = args.hostname[0]
recording_id = args.recording_id[0]
custom_dest = hasattr(args, 'dest')
destination = "./%s" % recording_id if not hasattr(args, 'dest') else args.dest[0]

if hasattr(args, 'log'):
    logging.basicConfig(level=logging.INFO)

logging.info("downloading %s from %s", args.recording_id, args.hostname)

# 1. checking folder existence
if not os.path.exists(destination):
    os.mkdir(destination)

# 1. fetching metadata
metadata_file = destination + "/metadata.xml"

if not os.path.exists(metadata_file):
    logging.info("downloading metadata.xml...")
    metadata_url = 'https://%s/presentation/%s/metadata.xml' % (hostname, recording_id)
    wget.download(metadata_url, out=metadata_file)
    print("\n")
else:
    logging.info("skipping metadata.xml...")

doc = xml.dom.minidom.parse(metadata_file)
state = doc.getElementsByTagName("state")[0].firstChild.data
published_flag = doc.getElementsByTagName("published")[0].firstChild.data
start_time = int(doc.getElementsByTagName("start_time")[0].firstChild.data)
end_time = int(doc.getElementsByTagName("end_time")[0].firstChild.data)
start_time_obj = datetime.datetime.fromtimestamp(start_time / 1000.0)
end_time_obj = datetime.datetime.fromtimestamp(end_time / 1000.0)
duration = (end_time - start_time)

meeting_name = doc.getElementsByTagName("meetingName")[0].firstChild.data

if (state != 'published') and (published_flag != 'true'):
    logging.error("Recording is not yet published.")
    exit(1)

start_time = doc.getElementsByTagName("start_time")[0].firstChild.data
end_time = doc.getElementsByTagName("end_time")[0].firstChild.data

# 2. Creating folders and downloading Files
logging.info("saving files to %s", destination)

if not os.path.exists(destination):
    os.mkdir(destination)

deskshare_target = destination + "/deskshare.webm"
if os.path.exists(deskshare_target):
    logging.warning("skipping deskshare...")
else:
    logging.info("downloading deskshare...")
    wget.download('https://%s/presentation/%s/deskshare/deskshare.webm' % (hostname, recording_id),
                  out=deskshare_target)
    print("\n")

video_target = destination + "/webcams.webm"
if os.path.exists(video_target):
    logging.warning("skipping webcam because webcams.webm already exists!")
else:
    logging.info("downloading webcam (with presentator audio)...")
    wget.download('https://%s/presentation/%s/video/webcams.webm' % (hostname, recording_id),
                  out=video_target)
    print("\n")


if not custom_dest:
    target_name = "%s_%s_%s" % (start_time_obj.strftime("%Y-%m-%d"), meeting_name, duration )
    os.rename(destination, target_name)

