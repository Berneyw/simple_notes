import note
from os import path


notes = note.Note()

base_dir = path.dirname(path.abspath(__file__))
commands_dir = path.join(base_dir, "..", "commands")

class SmartHelper:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SmartHelper, cls).__new__(cls)
        return cls._instance
    
    
    @classmethod
    def open_txt(cls, filename):
        try:
            with open(filename, "r") as file:
                return file.readlines()
        except FileNotFoundError:
            return "File not found!"
        
    @classmethod
    def LCSubStr(cls, X, Y, m, n):
        pass
        
    @classmethod
    def convert_list_to_int(cls, arr):
        arr = [str(integer) for integer in arr]
        a_string = "".join(arr)
        number = int(a_string)
        return number
    
    @classmethod
    def get_index_max_min_length(cls, arr):
        pass
        # min_length, min_idx, min_item = float('inf'), None, None

        # for i, item in enumerate(arr):
        #     if item:
        #         item_value = min(map(ord, item))
        #         if item_value == min(map(ord, arr)):
        #             item_length = len(item)
        #             if item_length < min_length:
        #                 min_length, min_idx, min_item = item_length, i, item

        # return arr[min_idx]


    def find_similar_command(self, user_input):
        pass
        # file_content = SmartHelper.open_txt("commands/all_commands.txt")
        # list_of_weights = []

        # max_weight = 0
        # max_weight_indices = []

        # for i in range(len(file_content)):
        #     weight = SmartHelper.LCSubStr(user_input, file_content[i], len(user_input), len(file_content[i]))
        #     list_of_weights.append(weight)

        #     if len(weight) > max_weight:
        #         max_weight = len(weight)
        #         max_weight_indices = [i]
        #     elif len(weight) == max_weight:
        #         max_weight_indices.append(i)

        # if max_weight_indices:
        #     return SmartHelper.get_index_max_min_length([file_content[i] for i in max_weight_indices])
        # else:
        #     return None
        

smart = SmartHelper()

# print(smart.find_similar_command("lisd"))


# if __name__ == "__main__":
#     note.main()
