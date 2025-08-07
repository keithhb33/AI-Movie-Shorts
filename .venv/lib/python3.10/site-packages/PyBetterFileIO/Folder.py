import re
import os
import shutil
from pathlib import Path

class Folder:

    def __init__(self, foldername):
        if "." not in foldername:
            self.foldername = foldername
        if "." in foldername:
            print("Please choose a folder/directory instead of a file with an extension (.txt, .html, etc.)")

    def exists(self):
        try:
            return os.path.isdir(self.foldername)
        except Exception as e:
            print(f"An error occured checking if {self.foldername} exists")

    def rename(self, new_foldername):
        try:
            if os.path.isdir(new_foldername):
                os.rmdir(new_foldername)
            os.rename(self.foldername, new_foldername)
            if os.path.isdir(self.foldername):
                path = Path(self.foldername)
                path.rename(new_foldername)
            print(f"Renamed {self.foldername} to {new_foldername}")
            self.foldername = new_foldername
            return self
        except FileNotFoundError:
            print(f"Folder/directory {self.foldername} does not exist at that location")
        except PermissionError:
            print(f"Permission denied renaming {self.foldername}")
        except Exception as e:
            print(f"An error occured while renaming {self.foldername}")

    def delete(self):
        try:
            if os.path.isdir(self.foldername):
                if len(self.foldername) > 0:
                    self.clear()
                os.rmdir(self.foldername)
            if (re.search(r'/.', self.foldername[1:]) or re.search(r'\\.', self.foldername[1:])):
                self.foldername = self.get_foldername()
            return self
        except FileNotFoundError:
            print(f"Folder/directory {self.foldername} does not exist at that location")
        except PermissionError:
            print(f"Permission denied deleting {self.foldername}")
        except Exception as e:
            print(f"An error occured while deleting {self.foldername}")

    def remove(self):
        return self.delete()

    def make(self):
        try:
            if os.path.isdir(self.foldername):
                #print(f"Folder/directory {self.foldername} already exists...continuing...")
                return self
            os.makedirs(self.foldername)
            return self
        except PermissionError:
            print(f"Permission denied while making {self.foldername}")
        except Exception as e:
            print(f"An error occured while making {self.foldername}")

    def create(self):
        return self.make()

    def copy_contents_to(self, new_foldername):
        try:
            if "." in new_foldername:
                return self
            if not os.path.isdir(new_foldername):
                self.make()
            files = os.listdir(self.foldername)
            for file in files:
                if os.path.isfile(os.path.join(self.foldername, file)):
                    shutil.copy(os.path.join(self.foldername, file), new_foldername)
                elif os.path.isdir(os.path.join(self.foldername, file)):
                    shutil.copytree(os.path.join(self.foldername, new_foldername))
            return self
        except FileNotFoundError:
            print(f"Folder/directory {self.foldername} does not exist at that directory")
        except PermissionError:
            print(f"Permission denied while copying {self.foldername}")
        except Exception as e:
            print(f"An error occured while copying {self.foldername} to {new_foldername}")
            print("Enter a new directory, including the new name")

    def copyContentsTo(self, new_foldername):
        return self.copy_contents_to()

    def copy_to(self, new_foldername):
        try:
            if not (new_foldername.strip().replace("/", "").replace("\\", "").endswith(self.foldername)):
                shutil.copytree(self.foldername, os.path.join(new_foldername, self.foldername))
            else:
                shutil.copytree(self.foldername, new_foldername)
            return self
        except FileNotFoundError:
            print(f"Folder/directory {self.foldername} does not exist at that directory")
        except PermissionError:
            print(f"Permission denied while copying {self.foldername}")
        except Exception as e:
            if "Cannot create a file when that file already exists" in str(e):
                return self
            print(f"An error occured while copying {self.foldername} to {new_foldername}: {e}")
            print("Enter a new directory, including the new name")

    def copyTo(self, new_foldername):
        return self.copy_to(new_foldername)
        

    def list(self):
        try:
            listed_files = os.listdir(self.foldername)
            return listed_files
        except FileNotFoundError:
            print(f"Folder/directory {self.foldername} does not exist at that location")
        except PermissionError:
            print(f"Permission denied while listing {self.foldername}")  
        except Exception as e:
            print(f"An error occurred while listing {self.foldername}")     

    def replace(self, folder_to_replace):
        try:
            try:
                Folder(folder_to_replace).delete()
            except Exception as e:
                pass
            self.copy_to(folder_to_replace)
            self.foldername = folder_to_replace
            return self
        except FileNotFoundError:
            print(f"Folder/directory {folder_to_replace} does not exist to replace at that location")
        except PermissionError:
            print(f"Permission denied while replacing {folder_to_replace} with {self.foldername}")
        except Exception as e:
            print(f"An error occurred while replacing {folder_to_replace} with {self.foldername}")

    def clear(self):
        try:
            clear_dir = self.foldername
            if os.path.isdir(clear_dir):
                if len(os.listdir(clear_dir)) == 0:
                    return self

            files = os.listdir(clear_dir)
            for file in files:
                file_path = os.path.join(clear_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                if os.path.isdir(file_path):
                    os.rmdir(file_path)
            return self
            
        except FileNotFoundError:
            print(f"Folder/directory {self.foldername} does not exist")
        except PermissionError:
            print(f"Permission denied while clearing {self.foldername}")
        except Exception as e:
            print(f"An error occurred while clearing {self.foldername}")
                
    @staticmethod
    def clear_at(clear_dir):
        try:
            if os.path.isdir(clear_dir):
                if len(os.listdir(clear_dir)) == 0:
                    files = os.listdir(clear_dir)
                    for file in files:
                        file_path = os.path.join(clear_dir, file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                        if os.path.isdir(file_path):
                            os.rmdir(file_path)
        except FileNotFoundError:
            print(f"Folder/directory {clear_dir} does not exist")
        except PermissionError:
            print(f"Permission denied while clearing {clear_dir}")
        except Exception as e:
            print(f"An error occurred while clearing {clear_dir}")
    
    @staticmethod
    def mkdir(directory):
        Folder(directory).make()

    def move_to(self, new_location):
        if os.path.isfile(new_location):
            return self
        temp = self.foldername
        self.copy_to(new_location)
        self.foldername = temp
        self.delete()
        return self
    
    def moveTo(self, new_location):
        return self.move_to(new_location)

    def make_file(self, filename):
        try:
            f = open(f"{self.foldername}/{filename}", 'w')
            f.close()
            return self
        except FileNotFoundError:
            print(f"Folder/directory {self.foldername} does not exist")
        except PermissionError:
            print(f"Permission denied while making {filename}")
        except Exception as e:
            print(f"An error occurred while making {filename}")

    def create_file(self, filename):
        self.make_file()
        return self

    def get_foldername(self):
        try:
            if os.path.isdir(self.foldername):
                return self.foldername
            else:
                if "/" in self.foldername:
                    folder = self.foldername.split("/")
                elif "\\" in self.foldername:
                    folder = self.foldername.split("\\")
                else:
                    folder = [self.foldername]
                dir_str = ""
                for i, ele in enumerate(folder):
                    dir_str += folder[i]
                    if not os.path.isdir(dir_str):
                        dir_str = dir_str.replace(folder[i], "")
                        self.foldername = dir_str
                        break
                return self.foldername
        except Exception as e:
            print("An error occured when trying to retrieve folder name.")

    #def set_foldername(self, new_foldername):
    #    try:
    #        self.foldername = new_foldername
    #        return self
    #    except Exception as e:
    #        print(f"An error occured while setting foldername to {new_foldername}")
            
