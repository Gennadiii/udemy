import os
import pyperclip
from re import search
from shutil import move

symbol_exceptions = '/\\*":?<>.\'|'


def get_txt(files):
    for file in files:
        if 'txt' in file and 'Link' not in file and 'link' not in file:
            print('\nLocated "' + base_dir + '    -    ' + file + '" txt file')
            return base_dir + '\\' + file


def replace_exception_symbols(text):
    for symbol in symbol_exceptions:
        if symbol == ':': text = text.replace(symbol, ' -')
        elif symbol == '.': text = text.replace(symbol, '')
        elif symbol == '?': text = text.replace(symbol, '')
        elif symbol == '***': text = text.replace(symbol, '_')
        else: text = text.replace(symbol, '_')
    return text


def get_info_from_txt(txt):
    result = {}
    section_count = 0
    lecture_count = 0
    current_section = None
    # f = open(txt, 'r')
    f = open(txt, 'r', encoding="utf8")
    lines = list(f)
    for j, line in enumerate(lines):
        if search(r'.*(: \d+)$', line):
            section_count += 1
            current_section = 'section' + str(section_count)
            section_name = lines[j + 2][:-1]  # Section name goes on the 3rd line after 'Раздел: 1'
            result[current_section] = {
                'name': str(section_count) + ' - ' + replace_exception_symbols(section_name),
                'lectures': []
            }
            print('\n\nFound section \t\t\t\t\t' + result[current_section]['name'] + '\n\n')
        if search(r'\d\. ', line):
            lecture_count += 1
            allowed_video_name = replace_exception_symbols(line[:-1])  # Remove \n
            result[current_section]['lectures'].append(allowed_video_name)
            print('Found lecture - ' + allowed_video_name)

    f.close()
    print('\n\n\n\t\t\t\t\tFound ' + str(section_count) + ' sections and ' + str(lecture_count) + ' lectures\n\n\n')
    return result


def create_sections_directories(course_structure):
    print('Creating directories for sections...')
    sections = course_structure.keys()
    for j, section in enumerate(sections):
        dir_name = course_structure[section]['name']
        if not os.path.exists(dir_name): os.mkdir(dir_name)


def get_downloaded_videos_dict(files):
    print('Getting downloaded videos dictionary...')
    count = 0
    current_lecture = None
    result = {}
    for file in files:
        if '.mp4' in file:
            count += 1
            current_lecture = 'lecture' + str(count)
            result[current_lecture] = {}
            video_name_without_id_and_extention = search(r'(.*)-\d*\.mp4', file).group(1)
            result[current_lecture]['pure_name'] = replace_exception_symbols(video_name_without_id_and_extention)
            result[current_lecture]['real_name'] = file
    return result


def move_renamed_files(course_structure, downloaded_videos):
    for video in downloaded_videos.keys():
        try:
            for section in course_structure.keys():
                for lecture in course_structure[section]['lectures']:
                    if downloaded_videos[video]['pure_name'] in lecture:
                        print('Moving "' + downloaded_videos[video]['real_name'] + '" to ' + course_structure[section][
                            'name'])
                        move(
                            downloaded_videos[video]['real_name'],
                            course_structure[section]['name'] + '\\' + lecture + '.mp4'
                        )
        except Exception as err:
            print('\n\tFailed to move file "' + downloaded_videos[video]['real_name'] + '": ' + str(err) + '\n')


def rename_rest_of_files(course_structure, downloaded_videos):
    move_renamed_files(course_structure, downloaded_videos, base_dir)


if __name__ == '__main__':
    try:
        base_dir = r'' + pyperclip.paste()
        os.chdir(base_dir)
        files = os.listdir()

        txt = get_txt(files)
        course_structure = get_info_from_txt(txt)
        downloaded_videos = get_downloaded_videos_dict(files)

        create_sections_directories(course_structure)
        move_renamed_files(course_structure, downloaded_videos)
    except Exception as err:
        print('Exiting with error: ' + str(err))
