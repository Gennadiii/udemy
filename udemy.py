import os
import pyperclip

videos_from_site = {}
downloaded_videos = {}
txt = None
folder = r'' + pyperclip.paste()
os.chdir(folder)
files = os.listdir()
bad_symbols = '/\\*":?<>'
sections = []
ffmpeg = r'C:\Program Files (x86)\ffmpeg-20170921-183fd30-win64-static\bin\ffmpeg.exe'


def locate_txt():
	for file in files:
		if 'txt' in file and 'Link' not in file and 'link' not in file:
			print(folder + '    -    ' + file)
			return folder + '\\' + file
txt = locate_txt()

def get_info_from_txt():
	f = open(txt, 'r')
	raw_list = list(f)
	raw_list_length = len(raw_list)
	for j in range(raw_list_length-1):
		video_name = raw_list[j][:-1] # Remove \n
		video_length = raw_list[j+1][:-1] # Remove \n
		if video_name[0].isdigit() and not '.' in video_length and video_length[0].isdigit():
			videos_from_site[video_length] = video_name
		if 'Раздел:' in raw_list[j]:
			sections.append( raw_list[j+2][:-1] )
	f.close()


def get_video_length_from_ffmpeg_response(file):
	print('Getting length of ' + file)
	file_not_deleted = True
	time = ''
	temp_ffmpeg_file = file.replace('mp4', 'txt')
	os.system(ffmpeg + ' -i ' + file + ' 2> ' + temp_ffmpeg_file)
	f = open(temp_ffmpeg_file, 'r')
	for j in range(100):
		line = f.readline()
		if 'Duration: ' in line:
			time = line[ line.find('Duration')+13 : line.find('Duration')+13+5 ]
			if time[0] == '0':
				time = time[1:]
				f.close()
				os.remove(temp_ffmpeg_file)
				file_not_deleted = False
				break
	f.close()
	if file_not_deleted:
		os.remove(temp_ffmpeg_file)
	return time


def get_info_from_dowloaded_videos():
	for file in files:
		if '.mp4' in file:
			downloaded_videos[get_video_length_from_ffmpeg_response(file)] = file


def remove_symbols(text):
	for symbol in bad_symbols:
		text = text.replace(symbol, '')
	return text


def increase_video_length_by_1sec(text):
	minutes = text[ : text.find(':') ]
	seconds = text[ text.find(':')+1 : ]
	if seconds == '59':
		seconds = '00'
		minutes = str( int(minutes) + 1 ).zfill(2)
	else:
		seconds = str( int(seconds) + 1 ).zfill(2)
	return minutes + ':' + seconds


def decrease_video_length_by_1sec(text):
	minutes = text[ : text.find(':') ]
	seconds = text[ text.find(':')+1 : ]
	if seconds == '00':
		seconds = '59'
		minutes = str( int(minutes) - 1 ).zfill(2)
	else:
		seconds = str( int(seconds) - 1 ).zfill(2)
	return minutes + ':' + seconds


# def rename_files():
# 	video_length_from_site_array = videos_from_site.keys()
# 	for video_length_from_site in video_length_from_site_array:
# 		try:
# 			if video_length_from_site not in downloaded_videos and increase_video_length_by_1sec(video_length_from_site) not in videos_from_site:

# 				videos_from_site[ increase_video_length_by_1sec(video_length_from_site) ] = videos_from_site[video_length_from_site]
# 				videos_from_site.pop(video_length_from_site)

# 				video_length_from_site = increase_video_length_by_1sec(video_length_from_site)

# 			os.rename( downloaded_videos[video_length_from_site], remove_symbols(videos_from_site[video_length_from_site]) + '.mp4' )
# 			downloaded_videos.pop(video_length_from_site)
# 		except Exception as err:
# 			print('Error ' + str(err))


def rename_files():
	video_length_from_site_array = videos_from_site.keys()
	for video_length_from_site in video_length_from_site_array:
		try:
			if video_length_from_site not in downloaded_videos:

				decreased_len = decrease_video_length_by_1sec(video_length_from_site)
				increased_len = increase_video_length_by_1sec(video_length_from_site)

				if decreased_len not in videos_from_site and decreased_len in downloaded_videos:
					videos_from_site[ decreased_len ] = videos_from_site[video_length_from_site]
					videos_from_site.pop(video_length_from_site)

				elif increased_len not in videos_from_site:
					videos_from_site[ increased_len ] = videos_from_site[video_length_from_site]
					videos_from_site.pop(video_length_from_site)

			os.rename( downloaded_videos[video_length_from_site], remove_symbols(videos_from_site[video_length_from_site]) + '.mp4' )
			downloaded_videos.pop(video_length_from_site)
		except Exception as err:
			print('Error ' + str(err))


def create_sections_directories():
	for j, section in enumerate(sections):
		os.mkdir( str(j+1) + ' - ' + remove_symbols(section) )


if __name__ == '__main__':
	get_info_from_txt()
	get_info_from_dowloaded_videos()
	rename_files()
	create_sections_directories()
