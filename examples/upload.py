from googled import Drive

with open('temp_file.txt', 'w') as f:
    f.write('hello world from Python with googld!')

p = Drive()
p.create_folder_if_not_exist('folder123')
p.listFiles(show_output=True)
p.upload2_folder_by_name('temp_file.txt', 'folder123')
