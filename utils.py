# import pyAesCrypt
# # encryption/decryption buffer size - 64K
# bufferSize = 64*1024
# password = "foopassword"
# # encrypt
# pyAesCrypt.encryptFile("rickroll.mp4", "rickroll.mp4.aes", password, bufferSize)
# # decrypt
# pyAesCrypt.decryptFile("rickroll.mp4.aes", "DECrickroll.mp4", password, bufferSize)

from string import ascii_letters, digits
import ffmpeg, os, cfg, time, schedule, threading
import random as rand
from app import db

def mp4_to_HLS(path, dest):
	input_stream = ffmpeg.input(path, f='mp4')
	output_stream = ffmpeg.output(input_stream, dest, format='hls', start_number=0, hls_time=5, hls_list_size=0, 
		segment_time=10, max_reload=10, hls_key_info_file="static/hls_keys/enc.keyinfo", loglevel="error")
	ffmpeg.run(output_stream)

def regenKey():
	seq = "".join([rand.choice(ascii_letters+digits) for i in range(16)])
	with open("static/hls_keys/enc(%s).key" % seq, "wb") as f:
		f.write(os.urandom(16))

	with open("static/hls_keys/enc.keyinfo", "w") as f:
		f.write("""../../hls_keys/enc(%s).key
static/hls_keys/enc(%s).key
\n%s""" % (seq, seq, seq))

regenKey()

def hlsThread():
	counter = 0
	while True:
		schedule.every(10).seconds.do(regenKey)
		schedule.run_continuously()

		videos = db.getNewVideos()
		for video in videos:
			ndir = "".join([rand.choice(ascii_letters+digits) for i in range(64)])
			os.mkdir(cfg.HLS_VIDEOS_FOLDER+ndir)
			try:
				db.update_video(video[-1], cfg.HLS_VIDEOS_FOLDER + ndir, status="in_progress")
				mp4_to_HLS(cfg.SOURCE_VIDEOS_FOLDER+video[0]+".mp4", cfg.HLS_VIDEOS_FOLDER + "%s/%s.m3u8" % (ndir, video[0]))
				db.update_video(video[-1], cfg.HLS_VIDEOS_FOLDER + ndir)
			except Exception as e:
				with open("log.log", 'a') as f:
					f.write(str(e))
				continue

		schedule.clear()

		time.sleep(15)

def runHlsThread():
    thread = threading.Thread(target=hlsThread, daemon=True)
    thread.start()



