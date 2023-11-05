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
    def LCSubStr(cls, string1, string2, length1, length2):
        # Create a table to store lengths of
        # longest common suffixes of substrings.
        # Note that LCSuff[i][j] contains the
        # length of longest common suffix of
        # X[0...i-1] and Y[0...j-1]. The first
        # row and first column entries have no
        # logical meaning, they are used only
        # for simplicity of the program.

        # LCSuff is the table with zero
        # value initially in each cell
        LCSuff = [[0 for k in range(length2 + 1)] for l in range(length1 + 1)]

        # To store the length of
        # longest common substring
        result = 0

        # Following steps to build
        # LCSuff[m+1][n+1] in bottom up fashion
        for i in range(length1 + 1):
            for j in range(length2 + 1):
                if i == 0 or j == 0:
                    LCSuff[i][j] = 0
                elif string1[i - 1] == string2[j - 1]:
                    LCSuff[i][j] = LCSuff[i - 1][j - 1] + 1
                    result = max(result, LCSuff[i][j])
                else:
                    LCSuff[i][j] = 0
        return result

    # @classmethod
    # def convert_list_to_int(cls, arr):
    #     arr = [str(integer) for integer in arr]
    #     a_string = "".join(arr)
    #     number = int(a_string)
    #     return number

    def find_similar_command(self, user_input):
        file_content = SmartHelper.open_txt("commands/all_commands.txt")
        # list with similarity based on longest common substring algorithm
        list_of_weights = []
        list_of_similar_words = []

        for i in file_content:
            weight = SmartHelper.LCSubStr(user_input, i, len(user_input), len(i))
            list_of_weights.append(weight)

        maximum = max(list_of_weights)
        
        if max(list_of_weights) < 2:
            return None
        # Get indeces of max values in list of weights
        max_indices = [
            index for index, value in enumerate(list_of_weights) if value == maximum
        ]
        for i in file_content:
            if file_content.index(i) in max_indices:
                list_of_similar_words.append(i)

        list_of_similar_words.sort(key=len)

        return list_of_similar_words[0]


smart = SmartHelper()

# if __name__ == "__main__":
#     note.main()
