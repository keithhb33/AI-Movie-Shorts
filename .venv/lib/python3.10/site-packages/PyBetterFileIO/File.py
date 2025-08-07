import os
import shutil
from pathlib import Path

class File:

    def __init__(self, filename):
        if "." not in filename:
            print("Please choose a file with an extension (.txt, .html, etc.)")
        if "." in filename:
            self.filename = filename
        elif type(filename) == "_io.TextIOWrapper":
            self.filename = os.path.join(os.path.dirname(self), os.path.basename(self))

    def exists(self):
        return os.path.isfile(self.filename)

    def rename(self, new_filename):
        try:
            if self.exists():
                os.rename(filename, new_filename)
                self.filename = new_filename
            return self
        except FileNotFoundError:
            print(f"File {self.filename} does not exist at that directory")
        except PermissionError:
            print(f"Permission denied renaming {self.filename}")
        except Exception as e:
            print(f"An error occured while renaming {self.filename}: {e}")

    def delete(self):
        try:
            os.remove(self.filename)
            return self
        except FileNotFoundError:
            print(f"File {self.filename} does not exist at that directory")
        except PermissionError:
            print(f"Permission denied deleting {self.filename}")
        except Exception as e:
            print(f"An error occured while deleting {self.filename}: {e}")

    def remove(self):
        try:
            self.delete()
            return self
        except FileNotFoundError:
            print(f"File {self.filename} does not exist at that directory")
        except PermissionError:
            print(f"Permission denied removing {self.filename}")
        except Exception as e:
            print(f"An error occured while removing {self.filename}: {e}")

    def make(self):
        try:
            if self.exists():
                #print(f"File {self.filename} already exists...continuing...")
                return self
            f = open(self.filename, 'w')
            f.close()
            return self
        except PermissionError:
            print(f"Permission denied while making {self.filename}")
        except Exception as e:
            print(f"An error occured while making {self.filename}: {e}")

    def create(self):
        try:
            self.make()
        except PermissionError:
            print(f"Permission denied while creating {self.filename}")
        except Exception as e:
            print(f"An error occured while creating {self.filename}: {e}")

    def copy(self, new_filename):
        try:
            shutil.copy2(self.filename, new_filename)
            return self
        except FileNotFoundError:
            print(f"File {self.filename} does not exist at that directory")
        except PermissionError:
            print(f"Permission denied while copying {self.filename}")
        except Exception as e:
            print(f"An error occured while copying {self.filename} to {new_filename}: {e}")

    def read(self):
        try:
            with open(self.filename, 'r', encoding="utf8") as file:
                return str(file.read())
        except FileNotFoundError:
            print(f"File {self.filename} does not exist at that directory")
        except PermissionError:
            print(f"Permission denied while reading {self.filename}")  
        except Exception as e:
            print(f"An error occurred while reading {self.filename}: {e}")

    def read_list(self):
        try:
            with open(self.filename, 'r', encoding="utf8") as file:
                return list(file.readlines())
        except FileNotFoundError:
            print(f"File {self.filename} does not exist at that directory")
        except PermissionError:
            print(f"Permission denied while reading {self.filename}")  
        except Exception as e:
            print(f"An error occurred while reading {self.filename}: {e}")

    def print(self):
        try:
            print(self.read())
            return self
        except FileNotFoundError:
            print(f"File {self.filename} does not exist at that directory")
        except PermissionError:
            print(f"Permission denied while printing {self.filename}")  
        except Exception as e:
            print(f"An error occurred while printing {self.filename}: {e}")

    def append(self, append_string):
        try:
            with open(self.filename, 'a') as file:
                file.write(append_string)
            return self
        except FileNotFoundError:
            print(f"File {self.filename} does not exist at that directory")
        except PermissionError:
            print(f"Permission denied while writing {append_string} to {self.filename}")
        except Exception as e:
            print(f"An error occurred while writing {append_string} to {self.filename}: {e}")

    def move_to(self, new_location):
        try:
            if ("." in new_location and "." != new_location[0] and "." != new_location[1] and len(new_location) > 2) or (new_location[0] == "." and not "." in new_location[1:]):
                if File(new_location).exists():
                    File(new_location).delete()
                shutil.move(self.filename, new_location)
                self.filename = new_location
            else:
                path = os.path.join(new_location, self.filename)
                if File(path).exists():
                    File(path).delete()
                shutil.move(self.filename, path)
                self.filename = path            
            return self
        except FileNotFoundError:
            print(f"File {self.filename} does not exist at that directory")
        except PermissionError:
            print(f"Permission denied while moving {self.filename} to {new_location}")
        except Exception as e:
            print(f"An error occurred while moving {self.filename} to {new_location}: {e}")

    def moveTo(self, new_location):
        return self.move_to(new_location)

    def write(self, write_string):
        try:
            self.clear()
            self.append(write_string)
            return self
        except FileNotFoundError:
            print(f"File {self.filename} does not exist at that directory")
        except PermissionError:
            print(f"Permission denied while writing {self.filename}")
        except Exception as e:
            print(f"An error occurred while writing {self.filename}: {e}")

    def replace(self, first_string, second_string, occurences=0):
            try:
                with open(self.filename, 'r') as file:
                    data = file.read()
                    if occurences != 0 or occurences < 0:
                        data = data.replace(first_string, second_string, occurences)
                    else:
                        while first_string in data:
                            data = data.replace(first_string, second_string)
                    with open(self.filename, 'w') as file:
                        file.write(data)
                return self
            except FileNotFoundError:
                print(f"File {self.filename} does not exist at that directory")
            except PermissionError:
                print(f"Permission denied while replacing {first_string} with {second_string} in {self.filename}")
            except Exception as e:
                print(f"An error occurred while replacing {first_string} with {second_string} in {self.filename}: {e}")

    def get_filename(self):
        return self.filename

    #def set_filename(self, new_filename):
    #    try:
    #        self.filename = new_filename
    #        return self
    #    except Exception as e:
    #        print(f"An error occured while setting filename to {new_filename}")")

    def copy_and_rename(self, new_file_name):
        try:
            shutil.copyfile(self.filename, new_file_name)
            return self
        except FileNotFoundError:
            print(f"File {self.filename} does not exist at that directory")
        except PermissionError:
            print(f"Permission denied while copying {self.filename} to {new_filename}")
        except Exception as e:
            print(f"An error occurred while copying {self.filename} to {new_filename}: {e}")

    def copyAndRename(self, newFileName):
        return self.copy_and_rename(newFileName)

    def copy_to(self, new_location):
        try:
            if ("." in new_location and "." != new_location[0] and "." != new_location[1] and len(new_location) > 2) or (new_location[0] == "." and not "." in new_location[1:]):
                if File(new_location).exists():
                    File(new_location).delete()
                shutil.copyfile(self.filename, new_location)
            else:
                path = os.path.join(new_location, self.filename)
                if File(path).exists():
                    File(path).delete()
                shutil.copy(self.filename, path)
            return self
        except FileNotFoundError:
            print(f"File {self.filename} does not exist at that directory")
        except PermissionError:
            print(f"Permission denied while moving {self.filename} to {new_location}")
        except Exception as e:
            print(f"An error occurred while moving {self.filename} to {new_location}: {e}")

    def copyTo(self, newFileName):
        return self.copy_to(newFileName)

    def get_default_file_object(self):
        default_file = open(self.filename)
        return default_file

    def getDefaultFileObject(self):
        return self.to_default_file_object()

    @staticmethod
    def get_custom_file_object(input_file):
        path = os.path.join(os.path.dirname(input_file.name), os.path.basename(input_file.name))
        return File(path)

    @staticmethod
    def getCustomFileObject(input_file):
        return File.get_custom_file_object(input_file)

    def clear(self):
        try:
            if self.exists():
                open(self.filename, 'w').close()
            return self
        except FileNotFoundError:
            print(f"File {self.outer_instance.filename} does not exist at that directory")
        except PermissionError:
            print(f"Permission denied while clearing {self.outer_instance.filename}")
        except Exception as e:
            print(f"An error occurred while clearing {self.outer_instance.filename}")
